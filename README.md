# GitHub Trending Tracker

每天自动获取 GitHub Trending 热门项目，生成报告并发送邮件通知。

## 功能

- 🔥 获取 GitHub Trending Daily Top 5
- 📊 获取 GitHub Trending Weekly Top 5
- 📄 生成 Markdown 和 JSON 格式报告
- 📧 通过 QQ 邮箱发送每日通知
- ⏰ GitHub Actions 定时自动运行

## 配置

### 1. Fork 本仓库

### 2. 配置 Secrets

在仓库的 Settings → Secrets and variables → Actions 中添加：

| Secret 名称 | 说明 |
|------------|------|
| `QQ_EMAIL` | 发送方 QQ 邮箱地址 |
| `QQ_EMAIL_PASSWORD` | QQ 邮箱授权码（非登录密码） |
| `TO_EMAIL` | 接收方邮箱地址 |

**获取 QQ 邮箱授权码：**
1. 登录 QQ 邮箱网页版
2. 设置 → 账户 → POP3/SMTP 服务
3. 开启服务并获取授权码

### 3. 启用 Actions

仓库的 Actions 默认启用，每天北京时间早上 7:00 自动运行。

也可以手动触发：Actions → Daily GitHub Trending → Run workflow

## 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 运行（不发送邮件）
python main.py

# 运行（发送邮件）
export QQ_EMAIL="your@qq.com"
export QQ_EMAIL_PASSWORD="your_auth_code"
export TO_EMAIL="receiver@example.com"
python main.py
```

## 数据存储

- `data/daily/YYYY-MM-DD.md` - 每日 Markdown 报告
- `data/daily/YYYY-MM-DD.json` - 每日 JSON 数据
- `data/latest.md` - 最新一期报告

## License

MIT
