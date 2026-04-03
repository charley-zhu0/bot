# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""
推推发送消息脚本

用法：
  # 发文本消息给用户
  uv run --env-file scripts/.env scripts/send_message.py --to-user zhulingqi --msgtype text --content "hello"

  # 发文本消息给群组
  uv run --env-file scripts/.env scripts/send_message.py --to-group 7653013246190869 --msgtype text --content "通知"

  # 发图片消息（需先上传获取 media_id）
  uv run --env-file scripts/.env scripts/send_message.py --to-user zhulingqi --msgtype image --media-id <media_id>

  # 发附件消息
  uv run --env-file scripts/.env scripts/send_message.py --to-user zhulingqi --msgtype attachment --media-id <media_id>

  # 发文本消息并 @ 群成员
  uv run --env-file scripts/.env scripts/send_message.py --to-group 7653013246190869 --msgtype text --content "hi" --at zhulingqi
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


def post(path: str, body: dict) -> dict:
    if not APPID or not SECRET:
        print("错误：TUITUI_APPID 和 TUITUI_SECRET 环境变量未设置")
        print("请使用 --env-file scripts/.env 参数运行，或手动设置环境变量")
        sys.exit(1)
    url = f"{BASE_URL}{path}?appid={APPID}&secret={SECRET}"
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"HTTP 错误 {e.code}: {e.reason}")
        sys.exit(1)
    except Exception as e:
        print(f"请求失败: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="推推发送消息脚本")

    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--to-user", metavar="ACCOUNT", help="发送给指定域账号（可多次使用）", action="append")
    target.add_argument("--to-group", metavar="GROUP_ID", help="发送给指定群组 ID（可多次使用）", action="append")

    parser.add_argument("--msgtype", required=True, choices=["text", "image", "attachment", "mixed"],
                        help="消息类型")
    parser.add_argument("--content", help="文本内容（msgtype=text 时必填）")
    parser.add_argument("--media-id", help="media_id（msgtype=image 或 attachment 时必填）")
    parser.add_argument("--at", metavar="ACCOUNT", help="@ 指定群成员域账号（仅发群时有效，可多次使用）",
                        action="append")
    args = parser.parse_args()

    body = {"msgtype": args.msgtype}

    if args.to_user:
        body["tousers"] = args.to_user
    else:
        body["togroups"] = args.to_group
        if args.at:
            body["at"] = args.at

    if args.msgtype == "text":
        if not args.content:
            parser.error("--content 是 msgtype=text 时的必填参数")
        body["text"] = {"content": args.content}
    elif args.msgtype == "image":
        if not args.media_id:
            parser.error("--media-id 是 msgtype=image 时的必填参数")
        body["image"] = {"media_id": args.media_id}
    elif args.msgtype == "attachment":
        if not args.media_id:
            parser.error("--media-id 是 msgtype=attachment 时的必填参数")
        body["attachment"] = {"media_id": args.media_id}
    elif args.msgtype == "mixed":
        parser.error("mixed 类型请使用 --content 传入 JSON 格式的 mixed 数组，暂不支持命令行构建")

    resp = post("/message/custom/send", body)
    if resp.get("errcode") == 0:
        print("消息已成功发送")
    else:
        print(f"发送失败: {resp.get('errmsg')} (errcode={resp.get('errcode')})")
        sys.exit(1)


if __name__ == "__main__":
    main()
