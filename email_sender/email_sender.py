"""
邮件发送模块
简单易用的 Python 邮件发送工具

用法:
    from email_sender import send_email
    
    # 发送邮件
    send_email(
        subject="邮件主题",
        content="邮件正文内容",
        to="收件人@example.com"  # 可选，默认发送到自定义列表
    )
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Union

# ==================== 配置区域 ====================
# 请根据你的邮箱服务商填写以下配置

# SMTP 服务器地址
SMTP_SERVER = "smtp.qq.com"  # QQ邮箱示例
SMTP_PORT = 465  # QQ邮箱使用 465 或 587

# 你的邮箱账号
SENDER_EMAIL = "your_email@qq.com"

# SMTP 授权码（不是QQ密码，需要在邮箱设置中获取）
SMTP_PASSWORD = "your_authorization_code"

# 默认收件人列表
DEFAULT_RECIPIENTS = [
    "primary@example.com",
    "secondary@example.com"
]

# ==================== 邮件发送函数 ====================

def send_email(
    subject: str,
    content: str,
    to: Union[str, List[str], None] = None
) -> dict:
    """
    发送邮件
    
    参数:
        subject: 邮件主题
        content: 邮件正文内容
        to: 收件人邮箱，可以是:
            - str: 单个收件人
            - List[str]: 多个收件人
            - None: 使用默认收件人列表
    
    返回:
        dict: {"success": True/False, "message": "..."}
    """
    
    # 确定收件人
    if to is None:
        recipients = DEFAULT_RECIPIENTS
    elif isinstance(to, str):
        recipients = [to]
    else:
        recipients = to
    
    # 验证收件人
    if not recipients:
        return {"success": False, "message": "没有指定收件人"}
    
    try:
        # 创建邮件
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = SENDER_EMAIL
        msg['To'] = ', '.join(recipients)
        
        # 添加正文（支持 HTML）
        if '<html>' in content.lower():
            msg.attach(MIMEText(content, 'html', 'utf-8'))
        else:
            msg.attach(MIMEText(content, 'plain', 'utf-8'))
        
        # 连接 SMTP 服务器并发送
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SENDER_EMAIL, SMTP_PASSWORD)
            server.sendmail(SENDER_EMAIL, recipients, msg.as_string())
        
        return {
            "success": True, 
            "message": f"邮件已成功发送给: {', '.join(recipients)}"
        }
        
    except smtplib.SMTPAuthenticationError:
        return {"success": False, "message": "SMTP 认证失败，请检查用户名和授权码"}
    except smtplib.SMTPException as e:
        return {"success": False, "message": f"SMTP 错误: {str(e)}"}
    except Exception as e:
        return {"success": False, "message": f"发送失败: {str(e)}"}


def send_email_with_cc(
    subject: str,
    content: str,
    to: Union[str, List[str]],
    cc: Union[str, List[str], None] = None
) -> dict:
    """
    发送邮件（支持抄送）
    
    参数:
        subject: 邮件主题
        content: 邮件正文内容
        to: 收件人
        cc: 抄送人（可选）
    
    返回:
        dict: {"success": True/False, "message": "..."}
    """
    
    # 确定收件人
    if isinstance(to, str):
        recipients = [to]
    else:
        recipients = list(to)
    
    # 添加抄送人
    if cc:
        if isinstance(cc, str):
            recipients.append(cc)
        else:
            recipients.extend(cc)
    
    try:
        # 创建邮件
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = SENDER_EMAIL
        msg['To'] = ', '.join(to) if isinstance(to, list) else to
        
        if cc:
            msg['Cc'] = ', '.join(cc) if isinstance(cc, list) else cc
        
        # 添加正文
        if '<html>' in content.lower():
            msg.attach(MIMEText(content, 'html', 'utf-8'))
        else:
            msg.attach(MIMEText(content, 'plain', 'utf-8'))
        
        # 发送
        all_recipients = recipients + (list(cc) if cc and isinstance(cc, list) else [cc] if cc else [])
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SENDER_EMAIL, SMTP_PASSWORD)
            server.sendmail(SENDER_EMAIL, all_recipients, msg.as_string())
        
        return {"success": True, "message": "邮件发送成功"}
        
    except Exception as e:
        return {"success": False, "message": f"发送失败: {str(e)}"}


# ==================== 命令行入口 ====================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("用法: python email_sender.py <主题> <内容> [收件人]")
        print("示例: python email_sender.py '测试' '这是一封测试邮件' 'test@example.com'")
        sys.exit(1)
    
    subject = sys.argv[1]
    content = sys.argv[2]
    to = sys.argv[3] if len(sys.argv) > 3 else None
    
    result = send_email(subject, content, to)
    print(result["message"])
    sys.exit(0 if result["success"] else 1)
