#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agnes-Video-V2.0 视频生成
模型名: agnes-video-v2.0  (带小数点!)
流程:   POST /v1/videos 创建任务 -> GET /agnesapi?video_id= 轮询 -> 下载 url

🔴 关键修复: 视频地址在 result["url"]，不是 remixed_from_video_id（恒为 null）
仅用 Python 标准库 (urllib)，含 503 / SSL EOF 退避重试。
"""
import os
import sys
import json
import time
import base64
import argparse
import urllib.parse
import urllib.request
import urllib.error

CREATE_URL = "https://apihub.agnes-ai.com/v1/videos"
QUERY_BASE = "https://apihub.agnes-ai.com/agnesapi"
MODEL = "agnes-video-v2.0"


def _post_json(url: str, payload: dict, api_key: str, timeout=120) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Authorization", f"Bearer {api_key}")
    req.add_header("Content-Type", "application/json")
    last_err = None
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 503:
                last_err = f"503 video_queue_full"
                time.sleep(min(2 ** attempt * 3, 30))
                continue
            body = e.read().decode("utf-8", "ignore")
            sys.exit(f"CREATE HTTP {e.code}: {body}")
        except Exception as e:  # 含 SSL UNEXPECTED_EOF 等瞬时错误
            last_err = str(e)
            time.sleep(min(2 ** attempt * 3, 30))
            continue
    sys.exit(f"CREATE_FAILED after retries: {last_err}")


def _get_json(url: str, api_key: str, timeout=120) -> dict:
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {api_key}")
    last_err = None
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:  # SSL EOF / 瞬时 5xx
            last_err = str(e)
            time.sleep(min(2 ** attempt * 3, 30))
            continue
    sys.exit(f"QUERY_FAILED after retries: {last_err}")


def _read_local_image(path: str) -> str:
    ext = path.rsplit(".", 1)[-1].lower()
    mime = {
        "png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
        "webp": "image/webp", "gif": "image/gif",
    }.get(ext, "image/png")
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    return f"data:{mime};base64,{b64}"


def main():
    p = argparse.ArgumentParser(description="Agnes-Video-V2.0 generator")
    p.add_argument("--prompt", required=True)
    p.add_argument("--image", default=None, help="单图 URL 或本地图片路径（图生视频）")
    p.add_argument("--images", nargs="*", default=None, help="多图 URL 列表")
    p.add_argument("--mode", default=None, help="如 keyframes")
    p.add_argument("--width", type=int, default=1152)
    p.add_argument("--height", type=int, default=768)
    p.add_argument("--num-frames", type=int, default=81, help="<=441 且 8n+1")
    p.add_argument("--frame-rate", type=int, default=24)
    p.add_argument("--seed", type=int, default=None)
    p.add_argument("--negative-prompt", default=None)
    p.add_argument("--output", default="agnes_video.mp4")
    p.add_argument("--api-key", default=None)
    p.add_argument("--interval", type=int, default=5, help="轮询间隔秒")
    p.add_argument("--max-wait", type=int, default=1800, help="最长等待秒")
    args = p.parse_args()

    api_key = args.api_key or os.environ.get("AGNES_API_KEY")
    if not api_key:
        sys.exit("ERROR: 未设置 API Key。请设置环境变量 AGNES_API_KEY 或传 --api-key。")

    payload = {
        "model": MODEL,
        "prompt": args.prompt,
        "width": args.width,
        "height": args.height,
        "num_frames": args.num_frames,
        "frame_rate": args.frame_rate,
    }
    if args.seed is not None:
        payload["seed"] = args.seed
    if args.negative_prompt:
        payload["negative_prompt"] = args.negative_prompt

    if args.images:
        payload.setdefault("extra_body", {})["image"] = args.images
        if args.mode:
            payload["extra_body"]["mode"] = args.mode
    elif args.image:
        if os.path.exists(args.image):
            payload["image"] = _read_local_image(args.image)
        else:
            payload["image"] = args.image
        if args.mode:
            payload.setdefault("extra_body", {})["mode"] = args.mode

    created = _post_json(CREATE_URL, payload, api_key)
    video_id = created.get("video_id") or created.get("task_id") or created.get("id")
    if not video_id:
        sys.exit("NO_VIDEO_ID in create response: " + json.dumps(created, ensure_ascii=False))
    print(f"TASK_CREATED video_id={video_id} (status={created.get('status')})")

    waited = 0
    while waited < args.max_wait:
        res = _get_json(f"{QUERY_BASE}?video_id={urllib.parse.quote(str(video_id))}", api_key)
        status = res.get("status")
        print(f"status={status} progress={res.get('progress')} size={res.get('size')} seconds={res.get('seconds')}")
        if status == "completed":
            # 🔴 真实视频地址在 url，remixed_from_video_id 恒为 null
            url = res.get("url") or res.get("remixed_from_video_id")
            if not url:
                sys.exit("COMPLETED but no url: " + json.dumps(res, ensure_ascii=False))
            try:
                with urllib.request.urlopen(url, timeout=300) as r:
                    with open(args.output, "wb") as f:
                        f.write(r.read())
                print(f"SAVED {args.output} ({res.get('size')}, {res.get('seconds')}s)")
                return
            except Exception as e:
                sys.exit(f"DOWNLOAD_FAILED {url}: {e}")
        if status == "failed":
            sys.exit("TASK_FAILED: " + json.dumps(res, ensure_ascii=False))
        time.sleep(args.interval)
        waited += args.interval

    sys.exit("TIMEOUT waiting for video")


if __name__ == "__main__":
    main()
