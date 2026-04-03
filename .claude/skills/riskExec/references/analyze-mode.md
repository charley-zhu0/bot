# riskExec 分析模式（analyze）参考

分析模式用于对已经执行过 riskExec 的结果文件进行离线分析，计算精确率、召回率和 F1-score，并提供标签优化策略建议。

**注意：分析模式复用 `excel.input` 指向的是已有结果文件（包含 Suggestion 和 Label 列）。**

## 配置示例 1：列值模式

通过某列的值标记黑样本（违规样本）：

```yaml
excel:
  input: "/home/test/results/test_output_20260402T155000.xlsx"
  output: "/home/test/results"

analysis:
  blackSamples:
    type: "column-mark"
    columnName: "预期结果"   # Excel 中包含预期标注的列名
    blackValue: "违规"       # 该列等于此值时标记为黑样本
  passValue: "PASS"          # 接口返回通过时 Suggestion 列的值
  suggestionColumn: "Suggestion"
  labelColumn: "Label"
```

## 配置示例 2：行号范围模式

通过 Excel 行号区间标记黑样本：

```yaml
excel:
  input: "/home/test/results/test_output_20260402T155000.xlsx"
  output: "/home/test/results"

analysis:
  blackSamples:
    type: "row-range"
    value: "2-100, 150-200, 250"  # 闭区间，从1开始（第1行为表头，数据从第2行起）
  passValue: "PASS"
  suggestionColumn: "Suggestion"
  labelColumn: "Label"
```

## 执行命令

```bash
/home/charley/repo/atom-service/llmsec/tools/riskExec/bin/riskExec-linux-amd64 \
  -mode analyze \
  -config <config.yml路径>
```

## 分析结果

执行后在终端输出数据概览，并生成分析结果文件到 `excel.output` 目录：
```
<原文件名>_analyze_<时间戳>.xlsx
```

结果文件新增 Sheet，包含：
- 标签命中统计
- 三种优化策略：Max Precision、Max Recall、F1-Balance
