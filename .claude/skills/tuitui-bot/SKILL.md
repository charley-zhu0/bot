---
name: tuitui-bot
description: 发送消息给推推（TuiTui）聊天软件的群组。当用户想要发送消息到推推群、通知某个推推群组、向推推发送内容时，必须使用此 skill。触发词包括：发送消息到推推、通知推推群、推推发消息、发给推推的xxx群、发送xxx到推推等。只要用户提到"推推"并想发送任何内容，就应立即使用此 skill。
---

# 推推机器人（TuiTui Bot）发消息指南

## 群组名称与 ID 映射

以下是当前维护的群组列表（后期可持续迭代添加）：

| 群组名称 | 群组 ID |
|---------|--------|
| 测试 | 7653013246190869 |
| 模安研发 | 7652669649100000 |

## API 信息

- **接口地址**：`http://alarm.im.qihoo.net/message/custom/send?appid=2554621127&secret=79cc92269e764911a26a2889431e8802883d63be`
- **Method**：POST
- **Content-Type**：application/json

## 发消息步骤

1. **识别目标群组**：根据用户提到的群组名称，在上方映射表中找到对应的群组 ID。
   - 如果用户说"测试群"或"测试"，使用 ID `7653013246190869`
   - 如果用户说"模安研发"或"研发群"，使用 ID `7652669649100000`
   - 如果用户提到的群组不在映射表中，告知用户该群组暂未配置，并询问是否需要添加

2. **构造请求并发送**：使用 curl 发送 POST 请求：

```bash
curl -X POST "http://alarm.im.qihoo.net/message/custom/send?appid=2554621127&secret=79cc92269e764911a26a2889431e8802883d63be" \
  -H "Content-Type: application/json" \
  -d '{
    "togroups": ["<群组ID>"],
    "msgtype": "text",
    "text": {
      "content": "<消息内容>"
    }
  }'
```

3. **确认结果**：执行 curl 后，解析返回的 JSON 响应：
   - 检查 `errcode` 字段：`errcode=0` 表示发送成功，否则为失败
   - **成功**：告知用户消息已成功发送，可附上 `msgids` 中的消息 ID 作为确认
   - **失败**：明确告知用户发送失败，并说明失败原因（`errmsg` 字段的内容）

## 示例

用户说："发送'部署完成'消息给推推的测试群"

执行：
```bash
curl -X POST "http://alarm.im.qihoo.net/message/custom/send?appid=2554621127&secret=79cc92269e764911a26a2889431e8802883d63be" \
  -H "Content-Type: application/json" \
  -d '{"togroups": ["7653013246190869"], "msgtype": "text", "text": {"content": "部署完成"}}'
```

## 返回值说明

API 返回 JSON 格式，示例：
```json
{"trans_id":"0b6764dbd95a997e","appid":"2554621127","robot_uid":"7652944526713211","robot_account":"bot-3qJelsTa","robot_name":"模安消息通知机器人","robot_desc":"推送自动化部署，测试结果","errcode":0,"errmsg":"请求成功","time":"2026-04-01T18:19:04+08:00","msgids":[{"group":"7653013246190869","msgid":"7623733354957125689"}]}
```

- `errcode=0`：发送成功，告知用户"消息已成功发送"
- `errcode≠0`：发送失败，告知用户"消息发送失败，原因：{errmsg}"

## 注意事项

- 群组 ID 必须以字符串形式放在数组中：`["7653013246190869"]`
- 如需同时发送到多个群组，将多个 ID 放入数组：`["id1", "id2"]`
- 消息内容支持纯文本，直接写在 `text.content` 字段中
- 如果用户提到的群组不在映射表中，不要猜测 ID，而是明确告知用户
- **必须解析返回值**判断是否成功，不能假设请求一定成功
