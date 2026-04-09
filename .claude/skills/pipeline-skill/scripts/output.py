"""输出格式化工具"""

import json
import sys
from typing import Any

def format_json(data: Any, indent: int = 2) -> str:
    return json.dumps(data, indent=indent, default=str, ensure_ascii=False)

def format_table(data: list, columns: list | None = None) -> str:
    if not data:
        return "(no data)"

    if columns is None:
        columns = list(data[0].keys()) if isinstance(data[0], dict) else ["value"]

    widths = {col: len(col) for col in columns}
    for row in data:
        if isinstance(row, dict):
            for col in columns:
                val = str(row.get(col, ""))
                # 中文字符宽度粗略计算，避免错位
                char_width = sum(2 if ord(c) > 127 else 1 for c in val)
                widths[col] = max(widths[col], char_width)

    lines = []
    header = " | ".join(col.ljust(widths[col]) for col in columns)
    lines.append(header)
    lines.append("-+-".join("-" * widths[col] for col in columns))

    for row in data:
        if isinstance(row, dict):
            # 对齐处理
            row_vals = []
            for col in columns:
                val = str(row.get(col, ""))
                char_width = sum(2 if ord(c) > 127 else 1 for c in val)
                padding = widths[col] - char_width + len(val)
                row_vals.append(val.ljust(padding))
            line = " | ".join(row_vals)
        else:
            line = str(row)
        lines.append(line)

    return "\n".join(lines)

def format_output(data: Any, as_json: bool = False, quiet: bool = False) -> None:
    if quiet:
        if isinstance(data, dict) and "id" in data:
            print(data["id"])
        elif isinstance(data, list) and data and isinstance(data[0], dict) and "id" in data[0]:
            for item in data:
                print(item.get("id", ""))
        else:
            print(data if isinstance(data, str) else format_json(data))
        return

    if as_json:
        print(format_json(data))
        return

    if isinstance(data, dict):
        _print_dict(data)
    elif isinstance(data, list):
        if data and isinstance(data[0], dict):
            print(format_table(data))
        else:
            for item in data:
                print(item)
    else:
        print(data)

def _print_dict(data: dict, indent: int = 0) -> None:
    prefix = "  " * indent
    for key, value in data.items():
        if isinstance(value, dict):
            print(f"{prefix}{key}:")
            _print_dict(value, indent + 1)
        elif isinstance(value, list):
            print(f"{prefix}{key}: {', '.join(str(v) for v in value[:5])}")
            if len(value) > 5:
                print(f"{prefix}  ... and {len(value) - 5} more")
        else:
            print(f"{prefix}{key}: {value}")

def error(message: str, suggestion: str | None = None) -> None:
    print(f"[Error] {message}", file=sys.stderr)
    if suggestion:
        print(f"\n  {suggestion}", file=sys.stderr)


def success(message: str) -> None:
    print(f"[Success] {message}")


def warning(message: str) -> None:
    print(f"[Warning] {message}", file=sys.stderr)
