#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agnes Image 2.5 Flash - 文生图 / 图生图 / 多图合成
模型名: agnes-image-2.5-flash  (带小数点!)
API:   POST https://apihub.agnes-ai.com/v1/images/generations
Auth:  Bearer $AGNES_API_KEY

要点:
  - size 用档位 1K/2K/3K/4K，配合 ratio (1:1 3:4 4:3 16:9 9:16 2:3 3:2 21:9)
  - 图生图/多图合成的输入图必须放 extra_body.image (数组)
  - response_format 不能放顶层；文生图 b64 用 return_base64, 图生图 b64 用 extra_body.response_format
仅使用 Python 标准库 (urllib)，无需 pip install。
"""
import os
import sys
import json
import base64
import argparse
import urllib.request
import urllib.error

API_URL = "https://apihub.agnes-ai.com/v1/images/generations"
MODEL = "agnes-image-2.5-flash"
RATIOS = ("1:1", "3:4", "4:3", "16:9", "9:16", "2:3", "3:2", "21:9")
SIZES = ("1K", "2K", "3K", "4K")


def _post(payload: dict, api_key: str) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(API_URL, data=data, method="POST")
    req.add_header("Authorization", f"Bearer {api_key}")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=360) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "ignore")
        sys.exit(f"HTTP {e.code}: {body}")
    except Exception as e:
        sys.exit(f"REQUEST_ERROR: {e}")


def _to_data_uri(path: str) -> str:
    ext = path.rsplit(".", 1)[-1].lower()
    mime = {
        "png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
        "webp": "image/webp", "gif": "image/gif",
    }.get(ext, "image/png")
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    return f"data:{mime};base64,{b64}"


def _norm_image(v: str) -> str:
    """本地文件 -> Data URI；公网 URL 原样返回。"""
    return _to_data_uri(v) if os.path.exists(v) else v


def main():
    p = argparse.ArgumentParser(description="Agnes Image 2.5 Flash generator")
    p.add_argument("--prompt", required=True)
    p.add_argument("--size", default="1K",
                   help="档位 1K/2K/3K/4K（推荐），或 1024x768 等历史写法")
    p.add_argument("--ratio", default=None,
                   help="宽高比: " + " ".join(RATIOS) + "（默认 1:1）")
    p.add_argument("--image", nargs="*", default=None,
                   help="图生图/多图合成输入：公网 URL 或本地路径，可传多个")
    p.add_argument("--base64", action="store_true", help="请求 Base64 输出而非 URL")
    p.add_argument("--output", default="agnes_image.png")
    p.add_argument("--api-key", default=None)
    args = p.parse_args()

    api_key = args.api_key or os.environ.get("AGNES_API_KEY")
    if not api_key:
        sys.exit("ERROR: 未设置 API Key。请设置环境变量 AGNES_API_KEY 或传 --api-key。")

    if args.ratio and args.ratio not in RATIOS:
        sys.exit(f"ERROR: ratio 必须是 {RATIOS} 之一，收到 {args.ratio}")

    payload = {"model": MODEL, "prompt": args.prompt, "size": args.size}
    if args.ratio:
        payload["ratio"] = args.ratio

    if args.image:
        # 🔴 图生图/多图合成：输入图必须放 extra_body.image
        imgs = [_norm_image(x) for x in args.image]
        payload["extra_body"] = {
            "image": imgs,
            "response_format": "b64_json" if args.base64 else "url",
        }
    elif args.base64:
        # 文生图 Base64：顶层 return_base64
        payload["return_base64"] = True

    res = _post(payload, api_key)
    item = (res.get("data") or [{}])[0]
    url, b64 = item.get("url"), item.get("b64_json")

    if b64:
        with open(args.output, "wb") as f:
            f.write(base64.b64decode(b64))
        print(f"SAVED_BASE64 {args.output} ({len(b64)} chars)")
    elif url:
        try:
            with urllib.request.urlopen(url, timeout=180) as r:
                with open(args.output, "wb") as f:
                    f.write(r.read())
            print(f"SAVED_URL {args.output}")
        except Exception as e:
            print(f"GOT_URL {url}  (下载失败: {e}，请手动下载)")
    else:
        print("NO_RESULT")
        print(json.dumps(res, ensure_ascii=False))


if __name__ == "__main__":
    main()
