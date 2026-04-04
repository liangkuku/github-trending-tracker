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
    将 Markdown 转换为 HTML 邮件格式
    
    优化：描述行单独显示，样式更易读
    """
    import re
    
    def convert_md_links(text: str) -> str:
        """将 Markdown 链接 [text](url) 转换为 HTML <a> 标签"""
        return re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
    
    lines = markdown.split("\n")
    html_lines = []
    in_table = False
    is_header_row = False
    
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
                html_lines.append("<table>")
                in_table = True
                is_header_row = True
            
            if "|:---" in line or "|---" in line:
                continue  # 跳过分隔行
            
            cells = [c.strip() for c in line.split("|")[1:-1]]
            
            # 检查是否是描述行（以 ↳ 开头）
            is_desc_row = len(cells) > 1 and cells[1].startswith("↳")
            
            if is_header_row:
                row = "".join(f"<th>{cell}</th>" for cell in cells)
                html_lines.append(f"<tr class='header'>{row}</tr>")
                is_header_row = False
            elif is_desc_row:
                # 描述行：合并单元格，特殊样式
                desc = cells[1][1:].strip()  # 去掉 ↳
                html_lines.append(f"<tr class='desc-row'><td></td><td colspan='4' class='desc'>{desc}</td></tr>")
            else:
                # 转换链接
                cells = [convert_md_links(cell) for cell in cells]
                row = "".join(f"<td>{cell}</td>" for cell in cells)
                html_lines.append(f"<tr>{row}</tr>")
        else:
            if in_table:
                html_lines.append("</table>")
                in_table = False
            if line.strip() and not line.startswith("---") and not line.startswith("*由"):
                html_lines.append(f"<p>{line}</p>")
    
    if in_table:
        html_lines.append("</table>")
    
    # 包装完整 HTML，优化样式
    body = "\n".join(html_lines)
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                padding: 20px;
                max-width: 800px;
                margin: 0 auto;
                background-color: #f6f8fa;
            }}
            h1 {{
                color: #24292f;
                border-bottom: 1px solid #d0d7de;
                padding-bottom: 10px;
            }}
            h2 {{
                color: #24292f;
                margin-top: 30px;
                font-size: 1.3em;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 15px 0;
                background-color: #fff;
                border-radius: 6px;
                overflow: hidden;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }}
            th {{
                background-color: #f6f8fa;
                color: #24292f;
                font-weight: 600;
                text-align: left;
                padding: 12px;
                border-bottom: 1px solid #d0d7de;
            }}
            td {{
                padding: 12px;
                border-bottom: 1px solid #d0d7de;
                vertical-align: top;
            }}
            tr:last-child td {{
                border-bottom: none;
            }}
            tr.desc-row td {{
                padding-top: 0;
                padding-bottom: 15px;
                border-bottom: 1px solid #d0d7de;
            }}
            .desc {{
                color: #57606a;
                font-size: 0.9em;
                line-height: 1.5;
            }}
            a {{
                color: #0969da;
                text-decoration: none;
                font-weight: 500;
            }}
            a:hover {{
                text-decoration: underline;
            }}
            blockquote {{
                color: #57606a;
                border-left: 3px solid #d0d7de;
                padding-left: 15px;
                margin: 15px 0;
            }}
        </style>
    </head>
    <body>
    {body}
    <p style="color: #57606a; font-size: 0.85em; margin-top: 30px; text-align: center;">
        由 GitHub Actions 自动生成
    </p>
    </body>
    </html>
    """
