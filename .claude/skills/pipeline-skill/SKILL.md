---
name: pipeline-skill
description: "极库云（geelib）流水线操作工具。支持运行流水线、查询运行状态、查询运行日志、取消流水线。当用户提到流水线、pipeline、CI/CD 构建、部署流水线、运行流水线、查看流水线状态或日志、取消流水线时使用此 skill。"
allowed-tools: Bash(uv *)
---

# 极库云流水线操作

通过 `uv run` 调用统一入口脚本 `${CLAUDE_SKILL_DIR}/scripts/pipeline.py` 操作流水线。

所有命令格式为：
```bash
uv run ${CLAUDE_SKILL_DIR}/scripts/pipeline.py <command> [options]
```

## 可用命令

| 命令       | 用途       | 必填参数                  | 可选参数                            |
|----------|----------|-------------------------|-----------------------------------|
| `run`    | 运行流水线    | `--pipeline-id <int>`   | `--real-set-params` `--remark`    |
| `status` | 查询运行状态   | `--id <运行记录ID>`         |                                   |
| `log`    | 查询运行日志   | `--id <运行记录ID>`         |                                   |
| `cancel` | 取消流水线    | `--exec-id <执行ID>`      |                                   |

## 使用示例

### 运行流水线（无参数）

```bash
uv run ${CLAUDE_SKILL_DIR}/scripts/pipeline.py run --pipeline-id 19316
```

### 运行流水线（带参数）

`--real-set-params` 接受一个 JSON 数组字符串，每个元素包含：
- `params_type`：参数类型（文本参数固定为 `"1"`）
- `params_name`：参数名称
- `params_value`：参数值
- `run_set`：是否运行时设置（固定为 `1`）

```bash
uv run ${CLAUDE_SKILL_DIR}/scripts/pipeline.py run --pipeline-id 18589 \
  --real-set-params '[{"params_type":"1","params_name":"a","params_value":"111","run_set":1},{"params_type":"1","params_name":"b","params_value":"222","run_set":1}]'
```

### 查询运行状态

```bash
uv run ${CLAUDE_SKILL_DIR}/scripts/pipeline.py status --id "69c9e1bfe71b8053074295f7"
```

### 查询运行日志

```bash
uv run ${CLAUDE_SKILL_DIR}/scripts/pipeline.py log --id "69c9e1bfe71b8053074295f7"
```

### 取消流水线

```bash
uv run ${CLAUDE_SKILL_DIR}/scripts/pipeline.py cancel --exec-id "69c9e1bfe71b8053074295f7"
```

## 典型工作流

1. 运行流水线 → 返回结果中包含运行记录 ID
2. 用运行记录 ID 查询状态
3. 若状态为"运行失败"，查询日志分析原因

## 状态码含义

| 值 | 含义   |
|----|--------|
| 0  | 等待中 |
| 1  | 运行中 |
| 2  | 运行成功 |
| 3  | 运行失败 |
| 4  | 已取消 |

## 认证配置

脚本从 `${CLAUDE_SKILL_DIR}/scripts/.env` 读取认证信息：
- `USER_MAIL`: 用户邮箱
- `TOKEN`: 私钥

## 排错

- **找不到 `.env`**：确认 `${CLAUDE_SKILL_DIR}/scripts/.env` 存在且包含 `USER_MAIL` 和 `TOKEN`
- **签名/鉴权失败**：检查 TOKEN 是否过期、USER_MAIL 是否匹配
- **查看帮助**：`uv run ${CLAUDE_SKILL_DIR}/scripts/pipeline.py --help`
