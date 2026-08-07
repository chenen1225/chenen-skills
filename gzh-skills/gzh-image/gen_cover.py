#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gzh-image: 公众号统一图像技能，生成封面 / 正文插图 / 带标注图解。
支持多供应商（封面用 gemini / nano banana 2，插图与图解用 gpt-image-2），
从 config.json 的 providers 读取；CLI 可覆盖 base_url/api_key/model/size。
diagram 角色复用 illustration 供应商（gpt-image-2）。

供应商类型 OpenAI 兼容：POST {base_url}/images/generations。
"""
import sys
import os
import time
import json
import base64
import argparse
import urllib.request
import urllib.error

SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SKILL_DIR, "config.json")


def load_cfg():
    if not os.path.exists(CONFIG_PATH):
        sys.exit("ERROR: config.json not found at " + CONFIG_PATH)
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


ROLE_ALIAS = {"diagram": "illustration"}


def build_provider(cfg, role, override_base, override_key, override_model):
    role = ROLE_ALIAS.get(role, role)
    providers = cfg.get("providers", {})
    if role and role in providers:
        p = dict(providers[role])
    else:
        # 兼容单 provider 旧写法
        p = {
            "base_url": cfg.get("base_url"),
            "api_key": cfg.get("api_key"),
            "model": cfg.get("model"),
            "size": cfg.get("size", "16:9"),
        }
    if override_base:
        p["base_url"] = override_base
    if override_key:
        p["api_key"] = override_key
    if override_model:
        p["model"] = override_model
    return p


def gen(prompt, out_path, prov, size=None, model=None):
    base = (prov.get("base_url") or "").rstrip("/")
    api_key = (prov.get("api_key") or "").strip()
    model = model or prov.get("model")
    size = size or prov.get("size", "16:9")

    if not base or not api_key or not model:
        sys.exit("ERROR: provider 缺少 base_url / api_key / model")
    if api_key.startswith("PASTE"):
        sys.exit("ERROR: api_key 未配置，请在 config.json 填入对应 key。")

    url = base + "/images/generations"
    body = {
        "model": model,
        "prompt": prompt,
        "n": 1,
        "size": size,
        "response_format": "b64_json",
    }
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + api_key,
        },
    )

    last_err = None
    # 429 限频自动退避重试（gpt-image-2 中继 1 分钟限 1 次）
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                res = json.loads(resp.read().decode("utf-8"))
            break
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "ignore")
            if e.code == 429:
                wait = 65 * (attempt + 1)
                sys.stderr.write("[429 限频] 第 %d 次重试，等待 %d 秒...\n" % (attempt + 1, wait))
                time.sleep(wait)
                last_err = "HTTP ERROR 429: " + detail[:2000]
                continue
            sys.exit("HTTP ERROR %s: %s" % (e.code, detail[:2000]))
        except Exception as e:  # noqa
            sys.exit("REQUEST FAILED: %s" % e)
    else:
        sys.exit("RETRY EXHAUSTED: " + (last_err or "unknown"))

    img_b64 = None
    img_url = None
    if isinstance(res, dict):
        data_list = res.get("data")
        if isinstance(data_list, list) and data_list:
            first = data_list[0]
            img_b64 = first.get("b64_json")
            img_url = first.get("url")

    if not img_b64 and not img_url:
        sys.exit("NO IMAGE IN RESPONSE. 完整返回:\n" + json.dumps(res, ensure_ascii=False)[:2000])

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    raw = base64.b64decode(img_b64) if img_b64 else urllib.request.urlopen(img_url, timeout=120).read()
    # 按真实文件头校正扩展名（中继常返回 JPEG 但 caller 写 .png）
    if raw[:3] == b"\xff\xd8\xff":
        real_ext = "jpg"
    elif raw[:8] == b"\x89PNG\r\n\x1a\n":
        real_ext = "png"
    else:
        real_ext = None
    if real_ext and not out_path.lower().endswith("." + real_ext):
        basep, _ = os.path.splitext(out_path)
        final_path = basep + "." + real_ext
    else:
        final_path = out_path
    with open(final_path, "wb") as f:
        f.write(raw)
    print("SAVED:", final_path)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt-file", required=True, help="英文图像 prompt 文本文件")
    ap.add_argument("--out", required=True, help="输出图片路径")
    ap.add_argument("--role", default=None, help="config.json providers 的键，如 cover / illustration / diagram")
    ap.add_argument("--base-url", default=None, help="覆盖 base_url")
    ap.add_argument("--api-key", default=None, help="覆盖 api_key")
    ap.add_argument("--model", default=None, help="覆盖 model，如 gpt-image-2 / gemini-3.1-flash-image")
    ap.add_argument("--size", default=None, help="覆盖画幅，如 16:9 / 21:9")
    args = ap.parse_args()
    with open(args.prompt_file, encoding="utf-8") as f:
        prompt = f.read().strip()
    cfg = load_cfg()
    prov = build_provider(cfg, args.role, args.base_url, args.api_key, args.model)
    gen(prompt, args.out, prov, size=args.size, model=args.model)
