---
name: riskExec
description: 使用 riskExec 工具对 Excel 测试集进行 API 并发评测并输出结果文件。当用户需要对风控接口/内容安全接口进行批量测试、提供了 curl 命令和 Excel 文件路径、或者想要生成带有 Suggestion/Label 字段的评测结果文件时，主动使用此技能。触发场景包括："帮我跑一下这个接口的评测"、"用这个 curl 命令测试 excel 里的数据"、"生成评测结果文件"、"帮我配置 riskExec"、"批量测试风控接口"。
---

# riskExec 评测 Skill

riskExec 是一个基于 Excel 数据驱动的 API 并发测试工具。用户通常只需提供一个 curl 命令和输入 Excel 文件路径，你负责生成 config.yml 并执行评测，最后告知用户结果文件位置。

## 可执行文件路径

```
/home/charley/repo/atom-service/llmsec/tools/riskExec/bin/riskExec-linux-amd64
```

这是已编译好的 Linux amd64 可执行文件，直接调用即可，无需重新编译。

## 用户需要提供的信息

1. **curl 命令**：包含 API 地址、请求头、form 字段
2. **输入 Excel 文件路径**：如 `/home/test/test.xlsx`
3. **额外输出字段**（可选）：除默认的 `suggest` 和 `labels` 之外的字段

如果用户没有提供某项，主动询问。

---

## 第一步：解析 curl 命令

从 curl 命令中提取以下信息：

| curl 元素 | 对应配置项 |
|-----------|-----------|
| URL（`'https://...'`） | `api.url` |
| `-k` / `--insecure` | `api.skipVerify: true` |
| `--header 'Key: Value'` | `api.headers` 下的键值对 |
| `--form 'key=value'` | `api.bodyTemplate` 中的字段 |
| `--form 'content=xxx'` | bodyTemplate 中替换为 `content={{prompt}}` |

**bodyTemplate 生成规则：**
- 将所有 `--form` 字段用 `&` 拼接，格式为 `key=value`
- `content` 字段的值固定替换为 `{{prompt}}`（Excel 中对应列名为 `prompt`）
- 其他字段保留原值（如 `trace_id=test123&app=test&location=default`）
- 数组类字段直接保留（如 `ability_list=["LLM-01","SW-01"]`）

**示例：**
```
curl -k --location --request POST 'https://10.253.91.154/api/moderate/text' \
  --header 'x-aisg-api-key: sk-abc123' \
  --form 'content=测试内容' \
  --form 'trace_id=test123' \
  --form 'app=test'
```
解析后：
```yaml
api:
  url: "https://10.253.91.154/api/moderate/text"
  skipVerify: true
  headers:
    x-aisg-api-key: "sk-abc123"
  contentType: "multipart/form-data"
  bodyTemplate: |
    content={{prompt}}&trace_id=test123&app=test
```

---

## 第二步：确定输出字段

**默认字段（始终包含，除非用户明确排除）：**

| 字段含义 | JSONPath | 输出列名 |
|---------|----------|---------|
| 建议动作（PASS/REJECT） | `$.result.suggest` | `Suggestion` |
| 安全标签 | `$.result.labels` | `Label` |

**用户额外指定的字段：**
- 若用户提到 `prompt`，其 JSONPath 为 `$.result.prompt`，列名为 `prompt`
- 若用户提到其他字段名，使用 `$.result.<字段名>` 作为 JSONPath，列名即字段名
- 若不确定 JSONPath，询问用户或查阅 `references/api-response-schema.md`

---

## 第三步：生成 config.yml

将 config.yml 保存到输入 Excel 文件所在目录，文件名格式：`config_<YYYYMMDD_HHMMSS>.yml`

完整模板：

```yaml
api:
  url: "<解析出的URL>"
  method: "POST"
  skipVerify: true
  timeout: 30
  headers:
    <header-key>: "<header-value>"
  contentType: "multipart/form-data"
  bodyTemplate: |
    <解析出的form字段，content替换为{{prompt}}>

excel:
  input: "<用户提供的输入文件绝对路径>"
  output: "<输入文件所在目录>/results"

execution:
  concurrency: 10
  interval: 0

extraction:
  fields:
    - path: "$.result.suggest"
      name: "Suggestion"
    - path: "$.result.labels"
      name: "Label"
    # 如有额外字段，追加在此处
```

生成后，将 config.yml 的完整内容展示给用户确认，询问："配置是否正确？确认后将开始执行评测。"

---

## 第四步：执行评测

```bash
# 1. 确保输出目录存在
mkdir -p "<输入文件目录>/results"

# 2. 执行评测
/home/charley/repo/atom-service/llmsec/tools/riskExec/bin/riskExec-linux-amd64 \
  -config "<config.yml路径>"
```

执行时可能耗时较长（取决于 Excel 行数和接口响应速度），告知用户正在执行中。

---

## 第五步：通知用户结果

执行完成后：
1. 告知用户结果文件位于 `<输入文件目录>/results/` 目录下
2. 结果文件名格式为 `<原文件名>_output_<时间戳>.xlsx`
3. 结果文件包含原始 Excel 所有列 + 新增的 `执行时间`、`状态`、`耗时(ms)` 列，以及 extraction 中配置的提取列（`Suggestion`、`Label` 等）

---

## 完整示例

**用户输入：**
```
当前风控的curl命令为：
curl -k --location --request POST 'https://10.253.91.154/llmsec/api/moderate/text' \
--header 'x-aisg-api-key: sk-911399152cbf11f1a2f9000c29f5fdf3' \
--form 'content=1989年暴动事件' \
--form 'trace_id=test123' \
--form 'app=test' \
--form 'ability_list=["LLM-01","SW-01","SW-02"]' \
--form 'location=default'
需要评测的文件为 /home/test/test.xlsx，输出字段需要包含 prompt、suggest 和 labels。
```

**生成的 config.yml（保存到 `/home/test/config_20260402_155000.yml`）：**
```yaml
api:
  url: "https://10.253.91.154/llmsec/api/moderate/text"
  method: "POST"
  skipVerify: true
  timeout: 30
  headers:
    x-aisg-api-key: "sk-911399152cbf11f1a2f9000c29f5fdf3"
  contentType: "multipart/form-data"
  bodyTemplate: |
    content={{prompt}}&trace_id=test123&app=test&ability_list=["LLM-01","SW-01","SW-02"]&location=default

excel:
  input: "/home/test/test.xlsx"
  output: "/home/test/results"

execution:
  concurrency: 10
  interval: 0

extraction:
  fields:
    - path: "$.result.suggest"
      name: "Suggestion"
    - path: "$.result.labels"
      name: "Label"
    - path: "$.result.prompt"
      name: "prompt"
```

**执行命令：**
```bash
mkdir -p /home/test/results
/home/charley/repo/atom-service/llmsec/tools/riskExec/bin/riskExec-linux-amd64 \
  -config /home/test/config_20260402_155000.yml
```

---

## 常见问题处理

### 用户没有提供 curl，只提供了 API 参数
按 curl 格式的参数逐项询问：URL、认证 header、form 字段列表。

### 用户想修改并发数或超时时间
在 config.yml 中调整 `execution.concurrency` 和 `api.timeout`。

### 用户想要分析模式（analyze）
分析模式用于计算精确率/召回率，配置方式不同，参见 `references/analyze-mode.md`。执行命令为：
```bash
./riskExec -mode analyze -config <config路径>
```

### 可执行文件报权限错误
```bash
chmod +x /home/charley/repo/atom-service/llmsec/tools/riskExec/bin/riskExec-linux-amd64
```

### 需要查看 Excel 内容（如确认列名）
如果需要确认 Excel 的列结构（尤其是 `prompt` 列是否存在），可使用 Python：
```bash
python3 -c "
import openpyxl
wb = openpyxl.load_workbook('<文件路径>', read_only=True)
ws = wb.active
headers = [cell.value for cell in next(ws.rows)]
print('列名:', headers)
"
```
如果 `openpyxl` 未安装，先运行 `pip install openpyxl`。

---

## 参考资料

- riskExec 完整文档：`/home/charley/repo/atom-service/llmsec/tools/riskExec/README.md`
- 配置示例：`/home/charley/repo/atom-service/llmsec/tools/riskExec/configs/config.yml`
- 分析模式详情：`references/analyze-mode.md`
