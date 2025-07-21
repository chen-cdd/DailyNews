# 📢 DailyNews：AI 自动资讯摘要与微信发布工具

> 自动抓取每日资讯、摘要重写、分析扩写，并生成适配公众号的 Markdown 和 HTML，支持一键上传微信草稿箱或预览。

---

## ✨ 项目特点

* 🔍 自动抓取微信公众号、企业官网等资讯页面
* 🧠 使用 OpenAI 模型生成摘要与扩写分析
* 📄 自动生成 Markdown 和美化 HTML（适配公众号）
* 🚀 一键推送至微信公众号草稿箱（支持草稿 / 预览 / 群发）
* 🕓 支持每日定时运行（基于 `schedule`）

---

## 📦 项目结构

```
.
├── main.py               # 主入口脚本，调度全流程
├── fetcher.py            # 支持微信公众号 / 通用网页的文章抓取
├── rewriter.py           # OpenAI 摘要生成与扩写
├── renderer.py           # 将文章列表渲染为 Markdown
├── md2html.py            # Markdown 转公众号样式 HTML
├── publisher.py          # 微信公众号草稿 / 群发管理
├── utils.py              # 配置读取、日志设置、已处理记录管理
├── test.py               # 获取粉丝 OpenID 工具脚本
├── config/
│   ├── urls.txt          # 手动输入模式的文章链接列表
│   └── settings.yaml     # API 密钥与发布参数配置
├── data/
│   ├── seen.json         # 已处理过的文章链接记录
│   ├── output/           # 输出 Markdown 和 HTML
│   └── logs/             # 日志记录
```

---

## ⚙️ 安装依赖

```bash
pip install -r requirements.txt
```

> 示例依赖包括：`openai`, `wechatpy`, `loguru`, `requests`, `bs4`, `markdown`, `pyyaml`

---

## 🚀 使用方法

### ▶ 手动模式（读取 `config/urls.txt`）

```bash
python main.py --manual
```

### ▶ 自动模式（从网站自动抓取）

```bash
python main.py --once
```

### ▶ 每日定时调度（默认每天早上 8:00）

```bash
python main.py
```

---

## 🔑 配置文件说明（`config/settings.yaml`）

```yaml
openai_api_key: "你的OpenAI API Key"
wechat_app_id: "你的微信公众号 app_id"
wechat_app_secret: "你的微信公众号 app_secret"
preview_openid: "测试预览用 openid"
extra_info: "我认为该技术的关键在于..."
thumb_path: "config/thumb.jpg"  # 封面图路径
```

---

## 📤 发布模式支持（可选项）

* `none`：不调用微信 API
* `draft_only`：只创建草稿（默认）
* `preview`：草稿 + 推送给指定用户预览
* `sendall`：草稿 + 群发（⚠危险操作）

配置方式见 `main.py` 中 `publish_mode` 参数说明。

---

## 🧪 粉丝 OpenID 查询（选填）

```bash
python test.py
```

用于获取你的微信粉丝 OpenID，用于预览发送。

---

## 📄 License

MIT License. 项目仅供学习使用，请勿泄露任何私钥。

