# AIchat - 狗头军师

一个基于 **Python + Flet** 开发的 AI 聊天桌面应用,内置"狗头军师"人设,擅长情感/关系问题分析,支持上传聊天截图让 AI 分析情绪与关系走向。

## 📌 致谢与出处

本项目中的"狗头军师"**人设与知识库**来自开源项目:

> **[powerycy/goutoujunshi](https://github.com/powerycy/goutoujunshi)**(⭐1.5k)
> 一个先接住情绪、再分析关系并给出可执行策略的 Codex 恋爱军师,内置心理、法律、社会、人文、哲学、婚姻家庭与性学知识库。

本项目 **AIchat** 是基于上述 skill 的 **Python 桌面应用化实现**:使用 Python + Flet 搭建了完整的聊天界面、记忆系统、图片分析等能力,并将该 skill 作为系统提示词接入 AI 对话。

**感谢原作者 [powerycy](https://github.com/powerycy) 的开源贡献。**

## ✨ 功能

- 💬 AI 对话(默认模型:google/gemma-4-31b-it,支持视觉)
- 📷 图片分析(上传聊天截图,AI 分析情绪与关系)
- 🧠 长期记忆(自动提取关键信息,跨会话记住用户)
- 📋 双击消息复制 / 文字选择复制
- 🔄 网络异常自动重试(3 次)
- 🎨 现代化聊天 UI(气泡、角色标签、Markdown 渲染、空状态欢迎页)

## 🔧 环境要求

- Python 3.10+
- 中转站 API(兼容 OpenAI 格式)

## 🚀 安装与运行

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

## ⚙️ 配置

复制 `.env.example` 为 `.env`:

```
AICHAT_API_KEY=你的API密钥
```

`config.py` 中可配置:

| 变量 | 说明 |
|------|------|
| `API_URL` | 中转站地址(OpenAI 兼容) |
| `MODEL` | 模型名(支持视觉的模型可看图) |

## 📦 打包成 exe

```bash
.venv\Scripts\flet pack chat.py --name AIchat --distpath dist
```

打包后需将 `skills/SKILL.md` 复制到 `dist/skills/` 目录(人设文件)。

## 📜 免责声明

本项目仅供学习交流使用,请遵守相关法律法规及 API 服务商的使用条款。AI 建议仅供参考,不替代专业心理咨询或法律意见。
