# 📧 Email Sender 模块安装指南

一个简单易用的 Python 邮件发送模块，支持自定义收件人列表。

---

## 📦 模块介绍

`email_sender` 是一个轻量级的 Python 邮件发送模块，特点：

- ✅ 仅一个文件，零依赖
- ✅ 支持 HTML 邮件
- ✅ 支持抄送（CC）
- ✅ 支持默认收件人列表
- ✅ 命令行友好

---

## 🛠️ 安装步骤

### 步骤 1：确保已安装 Python

```bash
python3 --version
```

如果显示版本号（如 `Python 3.9.6`），说明已安装。

---

### 步骤 2：获取 SMTP 授权码

不同的邮箱服务商，获取授权码的方式不同：

#### QQ 邮箱
1. 登录 [QQ 邮箱](https://mail.qq.com)
2. 点击 **设置** → **账户**
3. 找到 **POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV 服务**
4. 开启 **SMTP 服务**，获取授权码

#### 163 邮箱
1. 登录 [163 邮箱](https://mail.163.com)
2. 点击 **设置** → **POP3/SMTP/IMAP**
3. 开启 **SMTP 服务**，获取授权码

#### Gmail
1. 登录 Gmail
2. 进入 **Google 账户** → **安全**
3. 开启 **两步验证**
4. 生成 **应用专用密码**

---

### 步骤 3：配置模块

用文本编辑器打开 `email_sender.py`，修改配置区域：

```python
# ==================== 配置区域 ====================

# SMTP 服务器地址
SMTP_SERVER = "smtp.qq.com"      # QQ邮箱
SMTP_PORT = 465                  # 端口

# 你的邮箱账号
SENDER_EMAIL = "your_email@qq.com"

# SMTP 授权码
SMTP_PASSWORD = "your_authorization_code"

# 默认收件人列表（不指定收件人时使用）
DEFAULT_RECIPIENTS = [
    "primary@example.com",
    "secondary@example.com"
]
```

---

### 步骤 4：测试发送

```bash
cd email_sender

# 方式1：发送简单邮件
python3 email_sender.py "测试主题" "测试内容"

# 方式2：发送给指定收件人
python3 email_sender.py "测试" "内容" "someone@example.com"
```

---

## 💻 Python 代码中使用

```python
from email_sender import send_email

# 方式1：使用默认收件人列表
result = send_email(
    subject="每日汇总",
    content="今日工作完成情况：..."
)
print(result["message"])

# 方式2：发送给指定收件人
result = send_email(
    subject="会议通知",
    content="请于明天下午3点参加项目会议",
    to="colleague@example.com"
)

# 方式3：发送给多个收件人
result = send_email(
    subject="项目更新",
    content="本周项目进展报告",
    to=["user1@example.com", "user2@example.com"]
)

# 方式4：发送 HTML 邮件
result = send_email(
    subject="HTML 邮件",
    content="""
    <html>
        <body>
            <h1>标题</h1>
            <p>这是一个 <strong>HTML</strong> 邮件</p>
        </body>
    </html>
    """
)
```

---

## 📋 常用邮箱配置参考

| 邮箱服务商 | SMTP 服务器 | 端口 |
|-----------|------------|------|
| QQ 邮箱 | smtp.qq.com | 465 |
| 163 邮箱 | smtp.163.com | 465 |
| 126 邮箱 | smtp.126.com | 465 |
| Gmail | smtp.gmail.com | 587 |
| Outlook | smtp.office365.com | 587 |

---

## ⚠️ 常见问题

### Q: 提示 "SMTP 认证失败"
A: 检查授权码是否正确，或重新获取授权码。

### Q: 提示 "Connection timed out"
A: 检查 SMTP 服务器和端口是否正确，网络是否正常。

### Q: 收不到邮件
A: 检查垃圾邮件文件夹，或确认收件人邮箱地址正确。

---

## 📁 文件结构

```
your-project/
├── email_sender/
│   ├── email_sender.py    # 主模块
│   └── README.md         # 本文档
└── your_script.py        # 你的代码
```
