# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""
推推上传文件脚本（获取 media_id）

用法：
  # 上传图片
  uv run --env-file scripts/.env scripts/upload_media.py --type image --file /path/to/image.jpg

  # 上传附件（office/pdf/txt 等，不能是图片）
  uv run --env-file scripts/.env scripts/upload_media.py --type file --file /path/to/document.pdf
"""

import json
import sys
import os
import argparse
import urllib.request
import urllib.error

APPID = os.environ.get("TUITUI_APPID", "")
SECRET = os.environ.get("TUITUI_SECRET", "")
BASE_URL = "http://alarm.im.qihoo.net"


def upload(file_path: str, media_type: str) -> str:
    """上传文件，返回 media_id"""
    if not APPID or not SECRET:
        print("错误：TUITUI_APPID 和 TUITUI_SECRET 环境变量未设置")
        print("请使用 --env-file scripts/.env 参数运行，或手动设置环境变量")
        sys.exit(1)

    if not os.path.exists(file_path):
        print(f"错误：文件不存在: {file_path}")
        sys.exit(1)

    url = f"{BASE_URL}/media/upload?appid={APPID}&secret={SECRET}&type={media_type}"
    filename = os.path.basename(file_path)

    with open(file_path, "rb") as f:
        file_data = f.read()

    boundary = "----FormBoundary7MA4YWxkTrZu0gW"
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="media"; filename="{filename}"\r\n'
        f"Content-Type: application/octet-stream\r\n\r\n"
    ).encode("utf-8") + file_data + f"\r\n--{boundary}--\r\n".encode("utf-8")

    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"HTTP 错误 {e.code}: {e.reason}")
        sys.exit(1)
    except Exception as e:
        print(f"请求失败: {e}")
        sys.exit(1)

    if result.get("errcode") != 0:
        print(f"上传失败: {result.get('errmsg')} (errcode={result.get('errcode')})")
        sys.exit(1)

    media_id = result.get("media_id", "")
    print(f"上传成功，media_id: {media_id}")
    return media_id


def main():
    parser = argparse.ArgumentParser(description="推推上传文件脚本")
    parser.add_argument("--type", required=True, choices=["image", "file"], help="媒体类型：image（图片）或 file（附件）")
    parser.add_argument("--file", required=True, help="本地文件路径")
    args = parser.parse_args()

    upload(args.file, args.type)


if __name__ == "__main__":
    main()
