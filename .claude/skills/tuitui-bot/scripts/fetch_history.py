# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""
推推消息历史拉取脚本

通过推推 REST API 拉取群组或单聊的历史消息，支持分页，
保存为 Markdown 文件到 tmp/ 目录。

用法：
  # 拉取群消息
  uv run --env-file scripts/.env scripts/fetch_history.py --group <group_id> --start <YYYYMMDD> [--end <YYYYMMDD>]

  # 拉取单聊消息
  uv run --env-file scripts/.env scripts/fetch_history.py --user <域账号> --start <YYYYMMDD> [--end <YYYYMMDD>]

示例：
  uv run --env-file scripts/.env scripts/fetch_history.py --group 7652669649100000 --start 20260403
  uv run --env-file scripts/.env scripts/fetch_history.py --group 7652669649100000 --start 20260327 --end 20260403
  uv run --env-file scripts/.env scripts/fetch_history.py --user zhulingqi --start 20260403

输出文件命名：
  <start_YYYYMMDD-HHMM>_<end_YYYYMMDD-HHMM>-<group_id_or_user>.md
  保存在脚本同级的 ../tmp/ 目录下。
"""

import json
import sys
import os
import argparse
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta

APPID = os.environ.get("TUITUI_APPID", "")
SECRET = os.environ.get("TUITUI_SECRET", "")
BASE_URL = "http://alarm.im.qihoo.net"

CST = timezone(timedelta(hours=8))


def parse_date(date_str: str) -> datetime:
    """将 YYYYMMDD 解析为当天 00:00:00 CST"""
    return datetime.strptime(date_str, "%Y%m%d").replace(tzinfo=CST)


def to_api_time(dt: datetime) -> str:
    """转换为接口时间格式 2026-03-17T10:00:00+08:00"""
    return dt.strftime("%Y-%m-%dT%H:%M:%S+08:00")


def post(path: str, body: dict) -> dict:
    if not APPID or not SECRET:
        print("错误：TUITUI_APPID 和 TUITUI_SECRET 环境变量未设置")
        print("请使用 uv run --env-file scripts/.env scripts/fetch_history.py 运行")
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


def fetch_group(group_id: str, start: datetime, end: datetime) -> list:
    """分页拉取群消息，返回所有消息列表"""
    all_msgs = []
    cursor = "0"
    page = 1
    while True:
        print(f"  拉取第 {page} 页（cursor={cursor}）...", end=" ", flush=True)
        resp = post("/message/group/sync", {
            "group_id": group_id,
            "start_time": to_api_time(start),
            "end_time": to_api_time(end),
            "cursor": cursor,
            "limit": 100,
            "order_asc": True
        })
        if resp.get("errcode") != 0:
            print(f"\n接口返回错误: {resp.get('errmsg')}")
            sys.exit(1)
        msgs = resp.get("msgs", [])
        print(f"获取 {len(msgs)} 条")
        all_msgs.extend(msgs)
        if not resp.get("has_more"):
            break
        cursor = resp.get("cursor", "0")
        page += 1
    return all_msgs


def fetch_single(user: str, start: datetime, end: datetime) -> list:
    """分页拉取单聊消息，返回所有消息列表"""
    all_msgs = []
    cursor = "0"
    page = 1
    while True:
        print(f"  拉取第 {page} 页（cursor={cursor}）...", end=" ", flush=True)
        resp = post("/message/single/sync", {
            "user": user,
            "start_time": to_api_time(start),
            "end_time": to_api_time(end),
            "cursor": cursor,
            "limit": 100,
            "order_asc": True
        })
        if resp.get("errcode") != 0:
            print(f"\n接口返回错误: {resp.get('errmsg')}")
            sys.exit(1)
        msgs = resp.get("msgs", [])
        print(f"获取 {len(msgs)} 条")
        all_msgs.extend(msgs)
        if not resp.get("has_more"):
            break
        cursor = resp.get("cursor", "0")
        page += 1
    return all_msgs


def format_msg(msg: dict) -> str:
    """将消息 dict 格式化为 Markdown 表格行"""
    # 时间
    ts = msg.get("timestamp", "")
    try:
        dt = datetime.fromtimestamp(int(ts), tz=CST)
        time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        time_str = ts

    # 发送人
    user_name = msg.get("user_name", "")
    user_account = msg.get("user_account", "")
    if user_account:
        sender = f"{user_name}（{user_account}）"
    else:
        sender = user_name or "未知"

    # 内容（兼容新旧格式）
    event = msg.get("event", "")
    data = msg.get("data", {})

    # 新格式
    if data:
        msg_type = data.get("msg_type", "text")
        if msg_type == "text":
            content = data.get("text", "")
        elif msg_type == "image":
            content = "[图片]"
        elif msg_type == "file":
            f = data.get("file", {})
            content = f"[文件: {f.get('name', '未知')}]"
        elif msg_type == "voice":
            content = "[语音]"
        elif msg_type == "mixed":
            content = "[图文混排]"
        else:
            content = f"[{msg_type}]"
        ref = data.get("ref")
        if ref:
            ref_user = ref.get("user_name", "")
            ref_text = ref.get("text", "...")[:50]
            content += f" ↩引用{ref_user}: {ref_text}"
    else:
        # 旧格式兼容
        msg_type = msg.get("msgtype", "text")
        if msg_type == "text":
            content = msg.get("text", "")
        elif msg_type == "image":
            content = "[图片]"
        elif msg_type == "file":
            f = msg.get("file", {})
            content = f"[文件: {f.get('name', '未知')}]"
        else:
            content = f"[{msg_type}]"

    # 转义 Markdown 表格中的竖线
    content = content.replace("|", "｜").replace("\n", " ")

    return f"| {time_str} | {sender} | {content} |"


def save_markdown(msgs: list, target_id: str, target_type: str, start: datetime, end: datetime, output_dir: str) -> str:
    start_str = start.strftime("%Y%m%d-0000")
    end_str = end.strftime("%Y%m%d-2359")
    filename = f"{start_str}_{end_str}-{target_id}.md"
    filepath = os.path.join(output_dir, filename)
    os.makedirs(output_dir, exist_ok=True)

    label = "群组 ID" if target_type == "group" else "域账号"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# 推推消息历史\n\n")
        f.write(f"- **{label}**：{target_id}\n")
        f.write(f"- **时间范围**：{start.strftime('%Y-%m-%d 00:00')} 至 {end.strftime('%Y-%m-%d 23:59')}\n")
        f.write(f"- **生成时间**：{datetime.now(CST).strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"- **消息数量**：{len(msgs)} 条\n\n")
        f.write("## 消息记录\n\n")
        f.write("| 时间 | 发送人 | 内容 |\n")
        f.write("|------|--------|------|\n")
        for msg in msgs:
            f.write(format_msg(msg) + "\n")

    return filepath


def main():
    parser = argparse.ArgumentParser(description="推推消息历史拉取脚本")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--group", help="群组 ID")
    group.add_argument("--user", help="单聊域账号")
    parser.add_argument("--start", required=True, help="开始日期 YYYYMMDD")
    parser.add_argument("--end", help="结束日期 YYYYMMDD（默认与 start 相同）")
    parser.add_argument("--output-dir", default=None, help="输出目录（默认 ../tmp/）")
    args = parser.parse_args()

    start = parse_date(args.start)
    end = parse_date(args.end) if args.end else parse_date(args.start)
    # end 取当天 23:59:59
    end_time = end.replace(hour=23, minute=59, second=59)

    if args.output_dir:
        output_dir = args.output_dir
    else:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.normpath(os.path.join(script_dir, "..", "tmp"))

    if args.group:
        target_id = args.group
        target_type = "group"
        print(f"拉取群组 {target_id} 的消息")
        print(f"时间范围：{start.strftime('%Y-%m-%d')} 至 {end.strftime('%Y-%m-%d')}")
        msgs = fetch_group(target_id, start, end_time)
    else:
        target_id = args.user
        target_type = "single"
        print(f"拉取与 {target_id} 的单聊消息")
        print(f"时间范围：{start.strftime('%Y-%m-%d')} 至 {end.strftime('%Y-%m-%d')}")
        msgs = fetch_single(target_id, start, end_time)

    print(f"\n共拉取 {len(msgs)} 条消息")

    if msgs:
        filepath = save_markdown(msgs, target_id, target_type, start, end, output_dir)
        print(f"已保存至: {filepath}")
    else:
        print("无消息，未生成文件。")


if __name__ == "__main__":
    main()
