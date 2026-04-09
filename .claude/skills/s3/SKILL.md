---
name: s3
description: AWS S3 基础操作指南，包括列出所有 bucket、列出 bucket 下的所有对象、上传对象、下载对象、生成预签名 URL 等常用命令。支持通过环境变量切换多套 AWS 凭证。当用户需要操作 S3、管理存储桶或对象、生成临时访问链接、切换 AWS 账号/凭证时使用。
allowed-tools: Bash(aws s3*), Bash(aws s3api*), Bash(env *), Bash(export *)
---

# AWS S3 基础操作 Skill

本 skill 提供常用 AWS S3 操作的命令参考和执行能力，支持多套 AWS 凭证灵活切换。

---

## 凭证管理：多套 AWS Key 的使用方式

### 方式一：命令前临时指定（推荐，不污染环境）

在命令前直接内联环境变量，仅对本次命令生效：

```bash
AWS_ACCESS_KEY_ID=<key_id> \
AWS_SECRET_ACCESS_KEY=<secret> \
AWS_DEFAULT_REGION=<region> \
aws s3 ls
```

示例——用账号 A 的 Key 列出 bucket，同时不影响当前 shell 的凭证：
```bash
AWS_ACCESS_KEY_ID=AKIA... \
AWS_SECRET_ACCESS_KEY=xxxx \
AWS_DEFAULT_REGION=ap-northeast-1 \
aws s3 ls s3://my-bucket/
```

---

### 方式二：export 到当前 shell（影响后续所有命令）

切换到某套凭证后持续使用，直到再次 export 或关闭 shell：

```bash
# 切换到账号 A
export AWS_ACCESS_KEY_ID=<key_id_A>
export AWS_SECRET_ACCESS_KEY=<secret_A>
export AWS_DEFAULT_REGION=ap-northeast-1

# 后续所有 aws 命令都使用账号 A
aws s3 ls
aws s3 cp ...

# 切换到账号 B
export AWS_ACCESS_KEY_ID=<key_id_B>
export AWS_SECRET_ACCESS_KEY=<secret_B>
export AWS_DEFAULT_REGION=us-east-1
```

---

### 方式三：~/.aws/credentials named profile（适合固定多账号场景）

若需长期维护多账号，可在 `~/.aws/credentials` 中配置多个 profile：

```ini
[default]
aws_access_key_id = <key_id_default>
aws_secret_access_key = <secret_default>

[account-a]
aws_access_key_id = <key_id_A>
aws_secret_access_key = <secret_A>

[account-b]
aws_access_key_id = <key_id_B>
aws_secret_access_key = <secret_B>
```

使用时通过 `--profile` 参数或 `AWS_PROFILE` 环境变量指定：

```bash
# 使用 --profile 参数
aws s3 ls --profile account-a
aws s3 cp ./file.txt s3://my-bucket/ --profile account-b

# 或通过环境变量切换
export AWS_PROFILE=account-a
aws s3 ls
```

---

### 查看当前生效的凭证

```bash
# 查看当前使用的凭证身份（会显示 Account ID 和 UserId）
aws sts get-caller-identity

# 查看当前环境变量中的 AWS 相关配置
env | grep AWS
```

---

## 1. 列出所有 Bucket

```bash
aws s3 ls
```

使用 s3api 获取更详细信息：
```bash
aws s3api list-buckets --query "Buckets[*].{Name:Name,Created:CreationDate}" --output table
```

---

## 2. 列出 Bucket 下的所有对象

列出指定 bucket 的顶层内容：
```bash
aws s3 ls s3://<bucket-name>/
```

递归列出所有对象（包含子目录）：
```bash
aws s3 ls s3://<bucket-name>/ --recursive
```

列出指定前缀（目录）下的对象：
```bash
aws s3 ls s3://<bucket-name>/<prefix>/
```

使用 s3api 列出对象（支持分页）：
```bash
aws s3api list-objects-v2 \
  --bucket <bucket-name> \
  --prefix <prefix> \
  --query "Contents[*].{Key:Key,Size:Size,LastModified:LastModified}" \
  --output table
```

---

## 3. 上传对象

上传单个文件：
```bash
aws s3 cp <本地文件路径> s3://<bucket-name>/<目标路径>
```

上传并设置 Content-Type：
```bash
aws s3 cp <本地文件路径> s3://<bucket-name>/<目标路径> \
  --content-type "application/json"
```

上传整个目录（递归）：
```bash
aws s3 cp <本地目录> s3://<bucket-name>/<目标前缀>/ --recursive
```

同步本地目录到 S3（只上传新增/修改的文件）：
```bash
aws s3 sync <本地目录> s3://<bucket-name>/<目标前缀>/
```

上传并设置公开访问权限：
```bash
aws s3 cp <本地文件路径> s3://<bucket-name>/<目标路径> --acl public-read
```

使用 s3api 上传（支持更多元数据）：
```bash
aws s3api put-object \
  --bucket <bucket-name> \
  --key <对象键> \
  --body <本地文件路径> \
  --content-type "application/octet-stream" \
  --metadata '{"author":"john","env":"prod"}'
```

---

## 4. 下载对象

下载单个对象：
```bash
aws s3 cp s3://<bucket-name>/<对象键> <本地保存路径>
```

下载整个目录（递归）：
```bash
aws s3 cp s3://<bucket-name>/<前缀>/ <本地目录> --recursive
```

同步 S3 目录到本地：
```bash
aws s3 sync s3://<bucket-name>/<前缀>/ <本地目录>
```

使用 s3api 下载：
```bash
aws s3api get-object \
  --bucket <bucket-name> \
  --key <对象键> \
  <本地保存路径>
```

---

## 5. 生成预签名 URL

生成预签名下载 URL（默认有效期 3600 秒）：
```bash
aws s3 presign s3://<bucket-name>/<对象键>
```

指定有效期（秒），例如 7 天：
```bash
aws s3 presign s3://<bucket-name>/<对象键> --expires-in 604800
```

生成预签名上传 URL（PUT 操作，需使用 s3api）：
```bash
aws s3api generate-presigned-url \
  --bucket <bucket-name> \
  --key <对象键> \
  --http-method PUT \
  --expires-in 3600
```

生成预签名下载 URL（s3api 方式）：
```bash
aws s3api generate-presigned-url \
  --bucket <bucket-name> \
  --key <对象键> \
  --http-method GET \
  --expires-in 3600
```

---

## 6. 其他常用操作

### 删除对象
```bash
aws s3 rm s3://<bucket-name>/<对象键>
```

批量删除指定前缀下的所有对象：
```bash
aws s3 rm s3://<bucket-name>/<前缀>/ --recursive
```

### 复制/移动对象
```bash
# 复制
aws s3 cp s3://<源bucket>/<源键> s3://<目标bucket>/<目标键>

# 移动（复制后删除源文件）
aws s3 mv s3://<源bucket>/<源键> s3://<目标bucket>/<目标键>
```

### 查看对象元数据
```bash
aws s3api head-object --bucket <bucket-name> --key <对象键>
```

### 查看 Bucket 存储用量
```bash
aws s3 ls s3://<bucket-name>/ --recursive --human-readable --summarize
```

---

## 使用说明

执行操作前，按以下顺序确认信息：

1. **确认使用哪套凭证**：询问用户当前要用哪个 AWS_ACCESS_KEY_ID（或账号），优先使用「方式一：命令前临时指定」，避免污染当前 shell 环境。
2. **确认必要参数**：`<bucket-name>`、`<对象键>`、`<本地路径>`、`<region>` 等，缺少则先询问。
3. **破坏性操作需二次确认**：删除、批量删除等操作执行前必须向用户确认。

构造最终命令时，使用如下格式将凭证内联到命令前：
```bash
AWS_ACCESS_KEY_ID=<用户指定的key> \
AWS_SECRET_ACCESS_KEY=<对应的secret> \
AWS_DEFAULT_REGION=<region> \
aws s3 <具体操作>
```
