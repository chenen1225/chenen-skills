#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agnes Video 2.5 Flash 视频生成
模型 ID: agnes-video-2.5-flash  (带小数点!)
创建:    POST https://apihub.agnes-ai.com/v1/videos
查询:    GET  https://apihub.agnes-ai.com/agnesapi?video_id=<ID>&model_name=agnes-video-2.5-flash

🔴 关键: 最终视频地址在顶层 url（实测确证）；metadata 字段不存在；remixed_from_video_id 恒为 null
模式:    text(无媒体) / keyframe(first_frame|last_frame) / reference(images|audios)
仅用 Python 标准库 (urllib)。
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
MODEL = "agnes-video-2.5-flash"

RATIOS = ("21:9", "16:9", "4:3", "1:1", "3:4", "9:16")
MODES = ("text", "keyframe", "reference")


def _request(url, api_key, data=None, method=None, timeout=120):
    req = urllib.request.Request(url, data=data, method=method or ("POST" if data else "GET"))
    req.add_header("Authorization", f"Bearer {api_key}")
    if data:
        req.add_header("Content-Type", "application/json")
    last_err = None
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "ignore")
            if e.code in (429, 500, 503):
                last_err = f"HTTP {e.code}: {body}"
                time.sleep(min(2 ** attempt * 2, 30))
                continue
            sys.exit(f"HTTP {e.code}: {body}")
        except Exception as e:  # SSL EOF 等瞬时错误
            last_err = str(e)
            time.sleep(min(2 ** attempt * 2, 30))
            continue
    sys.exit(f"REQUEST_FAILED after retries: {last_err}")


def _to_data_uri(path: str) -> str:
    ext = path.rsplit(".", 1)[-1].lower()
    mime = {
        "png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
        "webp": "image/webp", "mp3": "audio/mpeg", "wav": "audio/wav",
        "m4a": "audio/mp4",
    }.get(ext, "application/octet-stream")
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    return f"data:{mime};base64,{b64}"


def _norm(v: str) -> str:
    """本地文件 -> Data URI；公网 URL 原样。"""
    return _to_data_uri(v) if os.path.exists(v) else v


def main():
    p = argparse.ArgumentParser(description="Agnes Video 2.5 Flash generator")
    p.add_argument("--prompt", required=True)
    p.add_argument("--mode", default="text", choices=MODES)
    p.add_argument("--seconds", default="5", help='字符串 "4"-"12"，默认 "5"')
    p.add_argument("--size", default="720P", help='Flash 固定 "720P"')
    p.add_argument("--aspect-ratio", default="16:9", choices=RATIOS)
    p.add_argument("--first-frame", default=None)
    p.add_argument("--last-frame", default=None)
    p.add_argument("--images", nargs="*", default=None, help="reference 模式参考图，最多 5 张")
    p.add_argument("--audios", nargs="*", default=None, help="reference 模式参考音频，最多 3 段")
    p.add_argument("--seed", type=int, default=None)
    p.add_argument("--output", default="agnes_video.mp4")
    p.add_argument("--api-key", default=None)
    p.add_argument("--interval", type=int, default=2, help="轮询间隔秒（建议 1-2）")
    p.add_argument("--max-wait", type=int, default=1800)
    args = p.parse_args()

    # ---- 本地校验 Flash 规则，避免 400 往返（先校验参数，再取 key）----
    if args.size != "720P":
        sys.exit(f'ERROR: Flash 的 size 必须为 "720P"，收到 {args.size}')
    if not (args.seconds.isdigit() and 4 <= int(args.seconds) <= 12):
        sys.exit(f'ERROR: seconds 必须是 "4"-"12" 的字符串，收到 {args.seconds}')

    payload = {
        "model": MODEL,
        "prompt": args.prompt,
        "mode": args.mode,
        "seconds": args.seconds,
        "size": args.size,
        "aspect_ratio": args.aspect_ratio,
    }
    if args.seed is not None:
        payload["seed"] = args.seed

    if args.mode == "text":
        if args.first_frame or args.last_frame:
            sys.exit("ERROR: text 模式不允许 first_frame / last_frame")
        if args.images or args.audios:
            sys.exit("ERROR: text 模式不允许 images / audios")
    elif args.mode == "keyframe":
        if not (args.first_frame or args.last_frame):
            sys.exit("ERROR: keyframe 模式需要 first_frame 或 last_frame 至少一个")
        if args.images or args.audios:
            sys.exit("ERROR: keyframe 模式不允许 images / audios")
        if args.first_frame:
            payload["first_frame"] = _norm(args.first_frame)
        if args.last_frame:
            payload["last_frame"] = _norm(args.last_frame)
    elif args.mode == "reference":
        if not (args.images or args.audios):
            sys.exit("ERROR: reference 模式需要 images 或 audios 至少一类非空")
        if args.first_frame or args.last_frame:
            sys.exit("ERROR: reference 模式不允许 first_frame / last_frame")
        if args.images:
            if len(args.images) > 5:
                sys.exit(f"ERROR: Flash 的 images 最多 5 张，收到 {len(args.images)}")
            payload["images"] = [_norm(x) for x in args.images]
        if args.audios:
            if len(args.audios) > 3:
                sys.exit(f"ERROR: Flash 的 audios 最多 3 段，收到 {len(args.audios)}")
            payload["audios"] = [_norm(x) for x in args.audios]

    # ---- 取 API Key（参数校验通过后再取，无需 key 也能提前拦住 400）----
    api_key = args.api_key or os.environ.get("AGNES_API_KEY")
    if not api_key:
        sys.exit("ERROR: 未设置 API Key。请设置环境变量 AGNES_API_KEY 或传 --api-key。")

    created = _request(CREATE_URL, api_key, data=json.dumps(payload).encode("utf-8"))
    video_id = created.get("video_id") or created.get("task_id") or created.get("id")
    if not video_id:
        sys.exit("NO_VIDEO_ID: " + json.dumps(created, ensure_ascii=False))
    print(f"TASK_CREATED video_id={video_id} status={created.get('status')} "
          f"seconds={created.get('seconds')} size={created.get('size')}")

    # 查询一律带 model_name（keyframe / reference 模式必需）
    query = f"{QUERY_BASE}?video_id={urllib.parse.quote(str(video_id))}&model_name={urllib.parse.quote(MODEL)}"
    waited = 0
    while waited < args.max_wait:
        res = _request(query, api_key)
        status = res.get("status")
        print(f"status={status} progress={res.get('progress')}")
        if status == "completed":
            meta = res.get("metadata") or {}
            # 🔴 实测：地址在顶层 url；metadata 字段可能不存在；remixed_from_video_id 恒为 null
            url = res.get("url") or meta.get("url")
            if not url:
                sys.exit("COMPLETED but video url missing: " + json.dumps(res, ensure_ascii=False))
            try:
                with urllib.request.urlopen(url, timeout=300) as r:
                    with open(args.output, "wb") as f:
                        f.write(r.read())
                print(f"SAVED {args.output} (size={res.get('size')}, seconds={res.get('seconds')})")
                return
            except Exception as e:
                sys.exit(f"DOWNLOAD_FAILED {url}: {e}")
        if status == "failed":
            err = (res.get("error") or {}).get("message")
            sys.exit(f"TASK_FAILED: {err or json.dumps(res, ensure_ascii=False)}")
        time.sleep(args.interval)
        waited += args.interval

    sys.exit("TIMEOUT waiting for video")


if __name__ == "__main__":
    main()
