#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agnes Image 2.1 Flash - 文生图 / 图生图
模型名: agnes-image-2.1-flash  (带小数点!)
API:   POST https://apihub.agnes-ai.com/v1/images/generations
Auth:  Bearer $AGNES_API_KEY

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
MODEL = "agnes-image-2.1-flash"


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
    except Exception as e:  # 网络抖动也退避一次
        sys.exit(f"REQUEST_ERROR: {e}")


SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(SKILL_DIR, "config.json")


def _load_config() -> dict:
    """本地密钥/默认参数。优先级（低->高）：config.json < 环境变量 < 命令行 --api-key。"""
    if not os.path.exists(CONFIG_PATH):
        return {}
    try:
        with open(CONFIG_PATH, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:  # noqa
        sys.stderr.write(f"[warn] config.json 读取失败: {e}\n")
        return {}


def _resolve_api_key(cli_key: str | None) -> str:
    cfg = _load_config()
    api_key = cli_key or os.environ.get("AGNES_API_KEY") or cfg.get("api_key")
    if not api_key:
        sys.exit(
            "ERROR: 未设置 API Key。任选其一：\n"
            f"  1) 写入 {CONFIG_PATH} 的 api_key 字段；\n"
            "  2) 设置环境变量 AGNES_API_KEY；\n"
            "  3) 命令行传 --api-key。"
        )
    return api_key
    ext = path.rsplit(".", 1)[-1].lower()
    mime = {
        "png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
        "webp": "image/webp", "gif": "image/gif",
    }.get(ext, "image/png")
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    return f"data:{mime};base64,{b64}"


def main():
    p = argparse.ArgumentParser(description="Agnes Image 2.1 Flash generator")
    p.add_argument("--prompt", required=True, help="生成 / 编辑提示词")
    p.add_argument("--size", default="1024x768", help="输出尺寸，如 1024x768")
    p.add_argument("--image", default=None, help="图生图输入：公网 URL 或本地图片路径")
    p.add_argument("--top-level-image", action="store_true",
                   help="把输入图放顶层 image（默认放 extra_body.image，见 SKILL.md 说明）")
    p.add_argument("--base64", action="store_true", help="文生图返回 Base64 而非 URL")
    p.add_argument("--output", default="agnes_image.png", help="输出文件名")
    p.add_argument("--api-key", default=None, help="不传则用环境变量 AGNES_API_KEY")
    args = p.parse_args()

    api_key = _resolve_api_key(args.api_key)

    payload = {
        "model": MODEL,
        "prompt": args.prompt,
        "size": args.size,
    }

    if args.image:
        if os.path.exists(args.image):
            img_val = _read_local_image(args.image)
        else:
            img_val = args.image
        if args.top_level_image:
            payload["image"] = [img_val]
        else:
            # 默认放 extra_body.image（与 2.5 文档一致，且与 2.1 接入方式兼容）
            payload.setdefault("extra_body", {})["image"] = [img_val]
            payload["extra_body"]["response_format"] = "b64_json" if args.base64 else "url"

    if args.base64:
        payload["return_base64"] = True

    res = _post(payload, api_key)
    item = (res.get("data") or [{}])[0]

    url = item.get("url")
    b64 = item.get("b64_json")

    if b64:
        with open(args.output, "wb") as f:
            f.write(base64.b64decode(b64))
        print(f"SAVED_BASE64 {args.output} ({len(b64)} chars)")
    elif url:
        try:
            with urllib.request.urlopen(url, timeout=120) as r:
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
