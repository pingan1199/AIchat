# AIchat - 狗头军师

一个基于 Python + Flet 的 AI 聊天桌面应用,内置"狗头军师"人设,擅长情感/关系问题分析。

> "狗头军师"人设与知识库来自开源项目 [powerycy/goutoujunshi](https://github.com/powerycy/goutoujunshi)(⭐1.5k),感谢原作者。

## 功能

- 💬 AI 对话(默认模型:google/gemma-4-31b-it,支持视觉)
- 📷 图片分析(上传聊天截图,AI 分析情绪与关系)
- 🧠 长期记忆(自动提取关键信息,跨会话记住用户)
- 📋 双击消息复制 / 文字选择复制
- 🔄 网络异常自动重试(3 次)
- 🎨 现代化聊天 UI(气泡、角色标签、Markdown 渲染、空状态欢迎页)

## 环境要求

- Python 3.10+
- 中转站 API(兼容 OpenAI 格式)

## 安装与运行

```bash
# 1. 创建虚拟环境
python -m venv .venv

# 2. 安装依赖
.venv\Scripts\pip install flet requests pillow python-dotenv

# 3. 配置密钥
# 复制 .env.example 为 .env,填入你的 API_KEY

# 4. 运行
.venv\Scripts\python chat.py
```

## 配置

复制 `.env.example` 为 `.env`:

```
AICHAT_API_KEY=你的API密钥
```

`config.py` 中可配置:

| 变量 | 说明 |
|------|------|
| `API_URL` | 中转站地址(OpenAI 兼容) |
| `MODEL` | 模型名(支持视觉的模型可看图) |

## 打包成 exe

```bash
.venv\Scripts\flet pack chat.py --name AIchat --distpath dist
```

打包后需将 `skills/SKILL.md` 复制到 `dist/skills/` 目录(人设文件)。

## 免责声明

本项目仅供学习交流使用,请遵守相关法律法规及 API 服务商的使用条款。
