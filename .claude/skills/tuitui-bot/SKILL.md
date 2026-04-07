---
name: tuitui-bot
description: 发送消息给推推（TuiTui）聊天软件的个人或群组，或拉取推推群组/单聊历史消息并汇总。当用户想要发送消息到推推、通知某个推推群、向推推某人发消息、发文字/图片/文件到推推时，必须使用此 skill。当用户想要拉取推推群历史消息、汇总某群某段时间的消息、查看推推群聊记录时，也必须使用此 skill。触发词包括：发送消息到推推、通知推推群、推推发消息、发给推推的xxx群、通过推推发给zhulingqi、推推通知、拉取推推消息、汇总推推群消息、拉取推推xxx群组当天的消息、帮我拉取最近7天的消息等。只要用户提到"推推"并想发送内容或查看/汇总群消息记录，就应立即使用此 skill。
---

# 推推机器人（TuiTui Bot）操作指南

## 环境配置

所有脚本通过 `uv run` 执行，凭证存储在 `.env` 文件中。

**凭证文件**：`scripts/.env`

```
TUITUI_APPID=xxx
TUITUI_SECRET=xxxx
```

**前置要求**：系统已安装 `uv`（[安装说明](https://docs.astral.sh/uv/getting-started/installation/)）

**运行方式**：所有脚本均使用以下格式调用（绝对路径）：

```bash
uv run --env-file /home/zhulingqi/repo/bot/.claude/skills/tuitui-bot/scripts/.env \
  /home/zhulingqi/repo/bot/.claude/skills/tuitui-bot/scripts/<script>.py [参数]
```

脚本使用 PEP 723 inline script metadata，uv 会自动管理依赖，无需提前创建虚拟环境。

---

## 群组名称与 ID 映射

| 群组名称 | 群组 ID |
|---------|--------|
| 测试 | 7653013246190869 |
| 模安研发 | 7652669649100000 |

- 用户说"测试群"或"测试" → ID `7653013246190869`
- 用户说"模安研发"或"研发群" → ID `7652669649100000`
- 用户直接提供数字 ID → 直接使用该 ID
- 用户提到的群组不在映射表中 → 告知用户暂未配置，询问是否需要添加

---

## 功能一：发送消息

使用脚本 `scripts/send_message.py`。

### 发送目标

支持两种发送目标，**不能混用**：

| 目标类型 | 参数 | 说明 |
|---------|------|------|
| 发给人 | `--to-user <域账号>` | 可多次使用，最多 100 人 |
| 发给群 | `--to-group <群组ID>` | 可多次使用，最多 10 个群 |

### 支持的消息类型

#### 1. 文本消息（text）

```bash
# 发给用户
uv run --env-file scripts/.env scripts/send_message.py \
  --to-user zhulingqi \
  --msgtype text \
  --content "消息内容"

# 发给群组
uv run --env-file scripts/.env scripts/send_message.py \
  --to-group 7652669649100000 \
  --msgtype text \
  --content "通知内容"

# 发给群组并 @ 某人
uv run --env-file scripts/.env scripts/send_message.py \
  --to-group 7652669649100000 \
  --msgtype text \
  --content "请注意" \
  --at zhulingqi
```

#### 2. 图片消息（image）

图片需先上传获得 `media_id`（见"上传文件"章节）：

```bash
uv run --env-file scripts/.env scripts/send_message.py \
  --to-user zhulingqi \
  --msgtype image \
  --media-id <media_id>
```

#### 3. 附件消息（attachment）

支持 office/pdf/txt 等（**不能是图片**）：

```bash
uv run --env-file scripts/.env scripts/send_message.py \
  --to-user zhulingqi \
  --msgtype attachment \
  --media-id <media_id>
```

### 发送结果判断

脚本自动解析返回值：
- 成功 → 输出 "消息已成功发送"
- 失败 → 输出错误信息并以非零状态码退出

---

## 功能二：上传文件（获取 media_id）

使用脚本 `scripts/upload_media.py`，上传成功后输出 `media_id`。

```bash
# 上传图片
uv run --env-file scripts/.env scripts/upload_media.py \
  --type image \
  --file /path/to/image.jpg

# 上传附件（office/pdf/txt 等，不能是图片）
uv run --env-file scripts/.env scripts/upload_media.py \
  --type file \
  --file /path/to/document.pdf
```

---

## 功能三：拉取历史消息

### 接口说明

| 场景 | 接口 |
|------|------|
| 拉群消息 | `POST /message/group/sync` |
| 拉单聊消息 | `POST /message/single/sync` |

### 使用脚本拉取

使用脚本 `scripts/fetch_history.py`，自动处理分页并生成 Markdown 文件。

```bash
# 拉取群组当天消息
uv run --env-file scripts/.env scripts/fetch_history.py \
  --group 7652669649100000 \
  --start 20260403

# 拉取群组最近7天消息
uv run --env-file scripts/.env scripts/fetch_history.py \
  --group 7652669649100000 \
  --start 20260327 \
  --end 20260403

# 拉取与某人的单聊消息
uv run --env-file scripts/.env scripts/fetch_history.py \
  --user zhulingqi \
  --start 20260403
```

**输出：** 消息自动保存到项目根目录的 `.tmp/` 文件夹，文件名格式：
```
<start_YYYYMMDD-HHMM>_<end_YYYYMMDD-HHMM>-<群ID或账号>.md
例：20260403-0000_20260403-2359-7652669649100000.md
```

### 拉取 + 汇总的完整步骤

1. **识别目标**：群组（名称→查映射表，或用户直接提供 ID）或单聊（域账号）
2. **确定时间范围**："今天"→ 当天日期，"最近7天"→ 从今天往前数7天
3. **运行脚本**：使用上方绝对路径格式执行脚本，等待脚本完成并输出文件路径
4. **读取文件**：读取 `.tmp/` 下生成的 `.md` 文件内容
5. **汇总**：对消息内容进行分析汇总，提炼关键信息、讨论主题、决策事项等呈现给用户

### 注意事项

- 机器人必须在目标群中，否则无法拉取群消息
- 脚本和 .env 文件的**绝对路径**：
  - 脚本目录：`/home/zhulingqi/repo/bot/.claude/skills/tuitui-bot/scripts/`
  - .env 文件：`/home/zhulingqi/repo/bot/.claude/skills/tuitui-bot/scripts/.env`
  - tmp 目录：`/home/zhulingqi/repo/bot/.tmp/`
- 如果消息量很大（上千条），汇总时重点关注关键决策、问题和结论，不必逐条列出
