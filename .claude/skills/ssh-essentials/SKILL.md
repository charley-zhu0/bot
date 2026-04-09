---
name: ssh-essentials
description: SSH 的基础命令，用于安全的远程访问、密钥管理、隧道转发和文件传输。
metadata: {"clawdbot":{"emoji":"🔐","requires":{"bins":["ssh"]}}}
---

# SSH 基础

Secure Shell（SSH）用于远程访问和安全文件传输。

## 基本连接

### 建立连接
```bash
# 使用用户名连接
ssh user@hostname

# 连接到指定端口
ssh user@hostname -p 2222

# 以详细输出模式连接
ssh -v user@hostname

# 使用指定密钥连接
ssh -i ~/.ssh/id_rsa user@hostname

# 连接并执行命令
ssh user@hostname 'ls -la'
ssh user@hostname 'uptime && df -h'
```

### 交互式使用
```bash
# 使用代理转发连接
ssh -A user@hostname

# 使用 X11 转发（GUI 应用）
ssh -X user@hostname
ssh -Y user@hostname  # 受信任的 X11

# 转义序列（在会话期间使用）
# ~.  - 断开连接
# ~^Z - 挂起 SSH
# ~#  - 列出已转发的连接
# ~?  - 帮助
```

## SSH 密钥

### 生成密钥
```bash
# 生成 RSA 密钥
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"

# 生成 ED25519 密钥（推荐）
ssh-keygen -t ed25519 -C "your_email@example.com"

# 使用自定义文件名生成
ssh-keygen -t ed25519 -f ~/.ssh/id_myserver

# 无口令生成（用于自动化）
ssh-keygen -t ed25519 -N "" -f ~/.ssh/id_deploy
```

### 管理密钥
```bash
# 将公钥复制到服务器
ssh-copy-id user@hostname

# 复制指定密钥
ssh-copy-id -i ~/.ssh/id_rsa.pub user@hostname

# 手动复制密钥
cat ~/.ssh/id_rsa.pub | ssh user@hostname 'cat >> ~/.ssh/authorized_keys'

# 检查密钥指纹
ssh-keygen -lf ~/.ssh/id_rsa.pub

# 修改密钥口令
ssh-keygen -p -f ~/.ssh/id_rsa
```

### SSH 代理
```bash
# 启动 ssh-agent
eval $(ssh-agent)

# 将密钥加入代理
ssh-add ~/.ssh/id_rsa

# 列出代理中的密钥
ssh-add -l

# 从代理中移除密钥
ssh-add -d ~/.ssh/id_rsa

# 移除所有密钥
ssh-add -D

# 设置密钥有效期（秒）
ssh-add -t 3600 ~/.ssh/id_rsa
```

## 端口转发与隧道

### 本地端口转发
```bash
# 将本地端口转发到远程
ssh -L 8080:localhost:80 user@hostname
# 通过以下地址访问：http://localhost:8080

# 转发到不同的远程主机
ssh -L 8080:database.example.com:5432 user@jumphost
# 通过 jumphost 访问数据库

# 多个转发
ssh -L 8080:localhost:80 -L 3306:localhost:3306 user@hostname
```

### 远程端口转发
```bash
# 将远程端口转发到本地
ssh -R 8080:localhost:3000 user@hostname
# 远程服务器可以通过其 8080 端口访问 localhost:3000

# 让服务可从远程访问
ssh -R 9000:localhost:9000 user@publicserver
```

### 动态端口转发（SOCKS 代理）
```bash
# 创建 SOCKS 代理
ssh -D 1080 user@hostname

# 在浏览器或应用中使用
# 配置 SOCKS5 代理：localhost:1080

# 配合 Firefox 使用
firefox --profile $(mktemp -d) \
  --preferences "network.proxy.type=1;network.proxy.socks=localhost;network.proxy.socks_port=1080"
```

### 后台隧道
```bash
# 在后台运行
ssh -f -N -L 8080:localhost:80 user@hostname

# -f: 后台运行
# -N: 不执行命令
# -L: 本地转发

# 保持连接存活
ssh -o ServerAliveInterval=60 -L 8080:localhost:80 user@hostname
```

## 配置

### SSH 配置文件（`~/.ssh/config`）
```
# 简单主机别名
Host myserver
    HostName 192.168.1.100
    User admin
    Port 2222

# 带密钥和选项
Host production
    HostName prod.example.com
    User deploy
    IdentityFile ~/.ssh/id_prod
    ForwardAgent yes
    
# 跳板机（bastion）
Host internal
    HostName 10.0.0.5
    User admin
    ProxyJump bastion

Host bastion
    HostName bastion.example.com
    User admin

# 通配符配置
Host *.example.com
    User admin
    ForwardAgent yes
    
# 保持连接存活
Host *
    ServerAliveInterval 60
    ServerAliveCountMax 3
```

### 使用配置
```bash
# 使用别名连接
ssh myserver

# 自动通过 bastion 跳转
ssh internal

# 覆盖配置选项
ssh -o "StrictHostKeyChecking=no" myserver
```

## 文件传输

### SCP（安全复制）
```bash
# 复制文件到远程
scp file.txt user@hostname:/path/to/destination/

# 从远程复制文件
scp user@hostname:/path/to/file.txt ./local/

# 递归复制目录
scp -r /local/dir user@hostname:/remote/dir/

# 使用指定端口复制
scp -P 2222 file.txt user@hostname:/path/

# 启用压缩复制
scp -C large-file.zip user@hostname:/path/

# 保留属性（时间戳、权限）
scp -p file.txt user@hostname:/path/
```

### SFTP（安全 FTP）
```bash
# 连接到 SFTP 服务器
sftp user@hostname

# 常用 SFTP 命令：
# pwd          - 远程工作目录
# lpwd         - 本地工作目录
# ls           - 列出远程文件
# lls          - 列出本地文件
# cd           - 切换远程目录
# lcd          - 切换本地目录
# get file     - 下载文件
# put file     - 上传文件
# mget *.txt   - 下载多个文件
# mput *.jpg   - 上传多个文件
# mkdir dir    - 创建远程目录
# rmdir dir    - 删除远程目录
# rm file      - 删除远程文件
# exit/bye     - 退出

# 批处理模式
sftp -b commands.txt user@hostname
```

### 通过 SSH 使用 Rsync
```bash
# 同步目录
rsync -avz /local/dir/ user@hostname:/remote/dir/

# 显示进度同步
rsync -avz --progress /local/dir/ user@hostname:/remote/dir/

# 同步并删除多余文件（镜像）
rsync -avz --delete /local/dir/ user@hostname:/remote/dir/

# 排除模式
rsync -avz --exclude '*.log' --exclude 'node_modules/' \
  /local/dir/ user@hostname:/remote/dir/

# 自定义 SSH 端口
rsync -avz -e "ssh -p 2222" /local/dir/ user@hostname:/remote/dir/

# 试运行
rsync -avz --dry-run /local/dir/ user@hostname:/remote/dir/
```

## 安全最佳实践

### 加固 SSH
```bash
# 禁用密码认证（编辑 /etc/ssh/sshd_config）
PasswordAuthentication no
PubkeyAuthentication yes

# 禁止 root 登录
PermitRootLogin no

# 更改默认端口
Port 2222

# 仅使用协议 2
Protocol 2

# 限制允许的用户
AllowUsers user1 user2

# 重启 SSH 服务
sudo systemctl restart sshd
```

### 连接安全
```bash
# 检查主机密钥
ssh-keygen -F hostname

# 删除旧的主机密钥
ssh-keygen -R hostname

# 严格检查主机密钥
ssh -o StrictHostKeyChecking=yes user@hostname

# 使用指定加密算法
ssh -c aes256-ctr user@hostname
```

## 故障排查

### 调试
```bash
# 详细输出
ssh -v user@hostname
ssh -vv user@hostname  # 更详细
ssh -vvv user@hostname  # 最大详细级别

# 测试连接
ssh -T user@hostname

# 检查权限
ls -la ~/.ssh/
# 应为：~/.ssh 为 700，密钥文件为 600，.pub 文件为 644
```

### 常见问题
```bash
# 修复权限
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_rsa
chmod 644 ~/.ssh/id_rsa.pub
chmod 644 ~/.ssh/authorized_keys

# 清除 known_hosts 条目
ssh-keygen -R hostname

# 禁用主机密钥检查（不推荐）
ssh -o StrictHostKeyChecking=no user@hostname
```

## 高级操作

### 跳板机（ProxyJump）
```bash
# 通过 bastion 连接
ssh -J bastion.example.com user@internal.local

# 多级跳转
ssh -J bastion1,bastion2 user@final-destination

# 使用配置文件（见上方“配置”章节）
ssh internal  # 自动使用 ProxyJump
```

### 连接复用
```bash
# 主连接
ssh -M -S ~/.ssh/control-%r@%h:%p user@hostname

# 复用连接
ssh -S ~/.ssh/control-user@hostname:22 user@hostname

# 在配置文件中：
# ControlMaster auto
# ControlPath ~/.ssh/control-%r@%h:%p
# ControlPersist 10m
```

### 执行命令
```bash
# 单条命令
ssh user@hostname 'uptime'

# 多条命令
ssh user@hostname 'cd /var/log && tail -n 20 syslog'

# 管道传递命令
cat local-script.sh | ssh user@hostname 'bash -s'

# 配合 sudo
ssh -t user@hostname 'sudo command'
```

## 提示

- 使用 SSH 密钥代替密码
- 对常用主机使用 `~/.ssh/config`
- 谨慎启用 SSH 代理转发（存在安全风险）
- 使用 ProxyJump 访问内部网络
- 保持 SSH 客户端和服务端为最新版本
- 使用 fail2ban 或类似工具防止暴力破解
- 监控 `/var/log/auth.log` 中的可疑活动
- 使用端口敲门或 VPN 增强安全性
- 安全备份你的 SSH 密钥
- 针对不同用途使用不同密钥

## 文档

官方文档：https://www.openssh.com/manual.html
Man 手册：`man ssh`、`man ssh_config`、`man sshd_config`
