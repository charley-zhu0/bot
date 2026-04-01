---
name: skill-editor-docs-mcp
description: 极库云知识中心MCP工具（editor-docs）调用指南，用于文档管理、编辑、搜索和知识库问答。当需要(1)创建或编辑文档、(2)搜索文档、(3)管理知识库空间、(4)获取或更新文档内容、(5)进行知识库问答、(6)生成测试用例、(7)查看文档版本差异、(8)浏览空间目录结构时使用此skill。支持ProseMirror JSON格式的文档操作。
---

# editor-docs MCP 工具调用指南
所有调用都需要通过editor-docs这个mcp服务实现。

## 认证要求

所有工具调用都需要提供认证信息：
- **user_mail** - 用户邮箱
- **user_token** - 用户令牌

认证方式：
1. HTTP请求头（推荐）：`user_mail: xxx@example.com`, `user_token: your_token`
2. URL查询参数：`?user_mail=xxx@example.com&user_token=your_token`

---

## 工具列表

### 1. search_doc_title_list - 根据标题搜索文档

**参数**：
- `title` (string, 必填) - 文档标题
- `pageNum` (number, 可选) - 页码，默认 1
- `pageSize` (number, 可选) - 每页数量，默认 10

**使用场景**：知道文档标题，快速定位文档

---

### 2. search_doc_list - 高级文档搜索

**参数**：
- `search` (string, 必填) - 文档关键字
- `spaceIds` (number[], 可选) - 空间ID数组
- `createName` (string, 可选) - 文档创建者
- `isMyCreateDoc` (boolean, 可选) - 是否仅查看我创建的文档，默认 false
- `pageNum` (number, 可选) - 页码，默认 1
- `pageSize` (number, 可选) - 每页数量，默认 10

**使用场景**：在特定空间内搜索、查找特定用户创建的文档、全文搜索

---

### 3. get_my_spaces - 获取用户空间列表

**参数**：
- `search` (string, 可选) - 搜索关键字
- `pageNum` (number, 可选) - 页码，默认 1
- `pageSize` (number, 可选) - 每页数量，默认 20

**使用场景**：创建文档前选择目标空间、查看可访问的空间列表

---

### 4. get_doc_content - 获取文档内容

**参数**：
- `docId` (number, 必填) - 文档ID
- `format` (string, 可选) - 返回格式：`json`（用于编辑）或 `markdown`（用于阅读），默认 `json`

**使用场景**：
- 编辑文档时使用 `json` 格式获取完整结构
- 阅读文档时使用 `markdown` 格式获得更好的可读性

---

### 5. update_doc_content - 更新文档内容

**参数**：
- `docId` (number, 必填) - 文档ID
- `content` (object, 必填) - ProseMirror JSON 格式的文档内容
  - `type` (string, 必填) - 必须是 `"doc"`
  - `content` (array, 必填) - 子节点数组

**使用场景**：修改现有文档内容、批量更新文档、替换文档全部内容

**注意**：大文档会自动分段处理（每批5个节点）

---

### 6. create_new_doc - 创建新文档

**参数**：
- `spaceId` (number, 必填) - 空间ID
- `title` (string, 可选) - 文档标题，默认 "未命名文档"
- `pid` (number, 可选) - 父文档ID，默认 0（空间根目录）

**使用场景**：在指定空间创建新文档、创建子文档

**注意**：创建后使用 `append_doc_content` 或 `update_doc_content` 添加内容

---

### 7. append_doc_content - 追加文档内容

**参数**：
- `docId` (number, 必填) - 文档ID
- `content` (object, 必填) - ProseMirror JSON 格式的文档内容
  - `type` (string, 必填) - 必须是 `"doc"`
  - `content` (array, 必填) - 要追加的子节点数组

**使用场景**：在文档末尾添加新内容、分批写入大文档、动态更新文档

**注意**：表格内容建议单独追加

---

### 8. get_doc_content_diff - 获取文档版本差异

**参数**：
- `docId` (number, 必填) - 文档ID

**使用场景**：查看文档修改历史、对比文档版本变化

---

### 9. question_doc - 知识库问答

**参数**：
- `question` (string, 必填) - 问题
- `isDeep` (boolean, 可选) - 是否进行深度搜索，默认 false

**使用场景**：询问知识库相关问题、获取文档内容的智能总结、快速查找特定信息

---

### 10. get_doc_test_plan - 生成测试用例

**参数**：
- `question` (string, 必填) - 主题
- `isDeep` (boolean, 可选) - 是否进行深度搜索，默认 false

**使用场景**：为功能模块生成测试用例、基于文档内容创建测试计划

---

### 11. get_space_directory_tree - 获取空间目录树

**参数**：
- `spaceId` (number, 必填) - 空间ID
- `pid` (number, 可选) - 父文档ID，默认 0（返回空间第一层）

**使用场景**：浏览空间文档结构、查找特定文档的位置

---

## ProseMirror 内容结构

### 根节点结构

所有文档内容必须以 `doc` 类型为根节点：

```json
{
  "type": "doc",
  "content": [
    // 子节点数组
  ]
}
```

### 常用节点类型

#### 段落 (paragraph)
```json
{
  "type": "paragraph",
  "content": [
    {
      "type": "text",
      "text": "这是一个段落"
    }
  ]
}
```

#### 标题 (heading)
```json
{
  "type": "heading",
  "attrs": {
    "level": 1
  },
  "content": [
    {
      "type": "text",
      "text": "一级标题"
    }
  ]
}
```

#### 代码块 (codeBlock)
```json
{
  "type": "codeBlock",
  "attrs": {
    "language": "javascript"
  },
  "content": [
    {
      "type": "text",
      "text": "console.log('Hello, World!');"
    }
  ]
}
```

#### 任务列表 (taskList)
```json
{
  "type": "taskList",
  "content": [
    {
      "type": "taskItem",
      "attrs": {
        "checked": false
      },
      "content": [
        {
          "type": "paragraph",
          "content": [
            {
              "type": "text",
              "text": "待办事项1"
            }
          ]
        }
      ]
    }
  ]
}
```

#### 表格 (table)
```json
{
  "type": "table",
  "content": [
    {
      "type": "tableRow",
      "content": [
        {
          "type": "tableHeader",
          "content": [
            {
              "type": "paragraph",
              "content": [
                {
                  "type": "text",
                  "text": "表头1"
                }
              ]
            }
          ]
        }
      ]
    },
    {
      "type": "tableRow",
      "content": [
        {
          "type": "tableCell",
          "content": [
            {
              "type": "paragraph",
              "content": [
                {
                  "type": "text",
                  "text": "单元格1"
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

#### 图片 (image)
```json
{
  "type": "image",
  "attrs": {
    "src": "https://example.com/image.png",
    "alt": "图片描述",
    "title": "图片标题"
  }
}
```

#### 引用块 (blockquote)
```json
{
  "type": "blockquote",
  "content": [
    {
      "type": "paragraph",
      "content": [
        {
          "type": "text",
          "text": "这是一段引用"
        }
      ]
    }
  ]
}
```

#### 列表 (bulletList / orderedList)
```json
{
  "type": "bulletList",
  "content": [
    {
      "type": "listItem",
      "content": [
        {
          "type": "paragraph",
          "content": [
            {
              "type": "text",
              "text": "列表项1"
            }
          ]
        }
      ]
    }
  ]
}
```

### 文本样式 (Marks)

#### 粗体 (bold)
```json
{
  "type": "text",
  "text": "粗体文本",
  "marks": [
    {
      "type": "bold"
    }
  ]
}
```

#### 斜体 (italic)
```json
{
  "type": "text",
  "text": "斜体文本",
  "marks": [
    {
      "type": "italic"
    }
  ]
}
```

#### 链接 (link)
```json
{
  "type": "text",
  "text": "链接文本",
  "marks": [
    {
      "type": "link",
      "attrs": {
        "href": "https://example.com",
        "target": "_blank"
      }
    }
  ]
}
```

#### 组合样式
```json
{
  "type": "text",
  "text": "粗体斜体链接",
  "marks": [
    {
      "type": "bold"
    },
    {
      "type": "italic"
    },
    {
      "type": "link",
      "attrs": {
        "href": "https://example.com"
      }
    }
  ]
}
```

---

## 资源模板

服务器提供多种 ProseMirror 文档模板，可通过资源 URI 访问：

### 可用模板

1. **prosemirror://basic-document** - 基本文档结构
2. **prosemirror://task-list/{items}/{checked}** - 待办事项列表
3. **prosemirror://table/{rows}/{cols}/{header}** - 表格
4. **prosemirror://code-block/{language}** - 代码块
5. **prosemirror://list/{type}/{items}** - 列表
6. **prosemirror://image/{src}/{alt}/{title}** - 图片
7. **prosemirror://blockquote/{content}** - 引用块
8. **prosemirror://horizontal-rule** - 分割线
9. **prosemirror://link/{text}/{href}/{target}** - 链接

---

## 常用工作流程

### 创建新文档
1. 调用 `get_my_spaces` 获取空间列表
2. 调用 `create_new_doc` 创建文档
3. 调用 `append_doc_content` 或 `update_doc_content` 添加内容

### 搜索并编辑文档
1. 调用 `search_doc_list` 或 `search_doc_title_list` 搜索文档
2. 调用 `get_doc_content` 获取文档内容（json格式）
3. 调用 `update_doc_content` 更新文档内容

### 知识库问答
1. 调用 `question_doc` 提问
2. 可选：基于回答创建文档并写入内容

---

## 注意事项

1. **内容结构**：所有文档内容必须以 `doc` 类型为根节点
2. **大文档处理**：`update_doc_content` 会自动分段处理（每批5个节点）
3. **表格处理**：表格内容建议单独追加
4. **格式选择**：编辑文档使用 `json` 格式，阅读文档使用 `markdown` 格式
5. **认证信息**：确保提供正确的 `user_mail` 和 `user_token`
6. **参数验证**：检查必填参数和参数格式是否符合要求

---

## 支持的节点类型

- `paragraph` - 段落
- `heading` - 标题（1-6级）
- `taskList` / `taskItem` - 任务列表
- `codeBlock` - 代码块
- `table` / `tableRow` / `tableCell` / `tableHeader` - 表格
- `bulletList` / `orderedList` / `listItem` - 列表
- `image` - 图片
- `blockquote` - 引用块
- `horizontalRule` - 分割线

## 支持的文本样式

- `bold` - 粗体
- `italic` - 斜体
- `underline` - 下划线
- `strike` - 删除线
- `link` - 链接