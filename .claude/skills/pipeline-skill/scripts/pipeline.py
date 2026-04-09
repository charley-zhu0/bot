#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "requests>=2.28.0",
#     "click>=8.1.0,<9",
# ]
# ///
"""极库云（geelib）流水线 CLI — 运行、查询状态、查询日志、取消流水线。"""

import json
import sys
from pathlib import Path

# 确保能从任意工作目录导入同级模块（client, config, output）
sys.path.insert(0, str(Path(__file__).parent))

import click
from client import LazyProjectClient
from output import error, success, format_output


@click.group()
@click.option("--debug", is_flag=True, help="出错时显示完整堆栈")
@click.pass_context
def cli(ctx, debug: bool):
    """极库云流水线操作工具"""
    ctx.ensure_object(dict)
    ctx.obj["debug"] = debug
    ctx.obj["client"] = LazyProjectClient()


@cli.command()
@click.option("--pipeline-id", type=int, required=True, help="流水线 ID")
@click.option("--real-set-params", default=None, help="执行参数（JSON 字符串）")
@click.option("--remark", default=None, help="运行备注")
@click.pass_context
def run(ctx, pipeline_id: int, real_set_params: str | None, remark: str | None):
    """触发运行一条流水线"""
    client = ctx.obj["client"]
    params = {"pipeline_id": pipeline_id}
    if real_set_params is not None:
        params["real_set_params"] = json.loads(real_set_params)
    if remark:
        params["remark"] = remark

    try:
        result = client.post("/openapi/Pipeline/compile", params)
        success("流水线运行触发成功")
        if result:
            format_output(result)
    except Exception as e:
        if ctx.obj["debug"]:
            raise
        error(f"流水线运行触发失败: {e}")
        sys.exit(1)


@cli.command()
@click.option("--id", "exec_id", required=True, help="流水线运行记录 ID")
@click.pass_context
def status(ctx, exec_id: str):
    """查询流水线运行状态"""
    client = ctx.obj["client"]
    params = {"id": exec_id}

    try:
        result = client.get("/api/v1/projects/geelib/openapi/getExecuteStatus/", params)
        status_map = {
            0: "等待中",
            1: "运行中",
            2: "运行成功",
            3: "运行失败",
            4: "已取消",
        }
        print(status_map.get(result, f"未知状态 ({result})"))
    except Exception as e:
        if ctx.obj["debug"]:
            raise
        error(f"获取流水线运行状态失败: {e}")
        sys.exit(1)


@cli.command()
@click.option("--id", "exec_id", required=True, help="流水线运行记录 ID")
@click.pass_context
def log(ctx, exec_id: str):
    """查询流水线运行日志"""
    client = ctx.obj["client"]
    params = {"id": exec_id}

    try:
        result = client.get("/api/v1/projects/geelib/openapi/pipelineInstanceLog", params)
        success("获取流水线运行日志成功")
        if result:
            format_output(result)
    except Exception as e:
        if ctx.obj["debug"]:
            raise
        error(f"获取流水线运行日志失败: {e}")
        sys.exit(1)


@cli.command()
@click.option("--exec-id", required=True, help="流水线执行 ID")
@click.pass_context
def cancel(ctx, exec_id: str):
    """取消正在运行的流水线"""
    client = ctx.obj["client"]
    params = {"exec_id": exec_id}

    try:
        result = client.post("/openapi/Pipeline/cancel", params)
        success("流水线取消成功")
        if result:
            format_output(result)
    except Exception as e:
        if ctx.obj["debug"]:
            raise
        error(f"流水线取消失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    cli()
