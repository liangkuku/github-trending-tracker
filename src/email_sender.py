"""QQ 邮箱发送模块"""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional


SMTP_SERVER = "smtp.qq.com"
SMTP_PORT = 465


def send_email(
    subject: str,
    html_content: str,
    to_email: Optional[str] = None,
    from_email: Optional[str] = None,
    password: Optional[str] = None,
) -> bool:
    """
    通过 QQ 邮箱发送邮件
    
    Args:
        subject: 邮件标题
        html_content: HTML 格式的邮件正文
        to_email: 收件人地址（默认从环境变量读取）
        from_email: 发件人地址（默认从环境变量读取）
        password: QQ 邮箱授权码（默认从环境变量读取）
    
    Returns:
        是否发送成功
    """
    # 从环境变量读取配置
    from_email = from_email or os.environ.get("QQ_EMAIL")
    password = password or os.environ.get("QQ_EMAIL_PASSWORD")
    to_email = to_email or os.environ.get("TO_EMAIL")
    
    if not all([from_email, password, to_email]):
        print("邮件配置不完整，跳过发送")
        return False
    
    try:
        # 创建邮件
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = from_email
        msg["To"] = to_email
        
        # 添加 HTML 内容
        html_part = MIMEText(html_content, "html", "utf-8")
        msg.attach(html_part)
        
        # 发送邮件
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(from_email, password)
            server.sendmail(from_email, to_email, msg.as_string())
        
        print(f"邮件发送成功: {to_email}")
        return True
        
    except Exception as e:
        print(f"邮件发送失败: {e}")
        return False


def markdown_to_html(markdown: str) -> str:
    """
    将 Markdown 转换为简单 HTML
    
    注意：这是简化版转换，只处理表格和基本格式
    """
    lines = markdown.split("\n")
    html_lines = []
    in_table = False
    
    for line in lines:
        # 标题
        if line.startswith("# "):
            html_lines.append(f"<h1>{line[2:]}</h1>")
        elif line.startswith("## "):
            html_lines.append(f"<h2>{line[3:]}</h2>")
        elif line.startswith("> "):
            html_lines.append(f"<blockquote>{line[2:]}</blockquote>")
        # 表格
        elif line.startswith("|"):
            if not in_table:
                html_lines.append("<table border='1' cellpadding='8' cellspacing='0' style='border-collapse: collapse;'>")
                in_table = True
            
            if "|:---" in line or "|---" in line:
                continue  # 跳过分隔行
            
            cells = [c.strip() for c in line.split("|")[1:-1]]
            row = "".join(f"<td>{cell}</td>" for cell in cells)
            html_lines.append(f"<tr>{row}</tr>")
        else:
            if in_table:
                html_lines.append("</table>")
                in_table = False
            if line.strip():
                html_lines.append(f"<p>{line}</p>")
    
    if in_table:
        html_lines.append("</table>")
    
    # 包装完整 HTML
    body = "\n".join(html_lines)
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; padding: 20px; }}
            h1 {{ color: #333; }}
            h2 {{ color: #555; margin-top: 30px; }}
            table {{ width: 100%; margin: 10px 0; }}
            td {{ padding: 8px; }}
            tr:nth-child(even) {{ background-color: #f9f9f9; }}
            a {{ color: #0366d6; text-decoration: none; }}
            blockquote {{ color: #666; border-left: 3px solid #ddd; padding-left: 10px; margin: 10px 0; }}
        </style>
    </head>
    <body>
    {body}
    </body>
    </html>
    """
