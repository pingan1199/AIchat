import requests
import json
import time
import asyncio
import flet as ft
import config
import os, sys
if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(BASE_DIR, "skills", "SKILL.md"), "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()
history = []
def chat_with_ai(history):
    headers = {
        "Authorization": f"Bearer {config.API_KEY}",
        "Content-Type": "application/json"
    }
    memory_text = ""
    if memory:
        memory_text = "\n\n【关于用户的长期记忆(你要记住)】\n" + "\n".join("- " + m for m in memory)
    messages = [{"role":"system","content":SYSTEM_PROMPT + memory_text}] + history[-20:]
    data = {

        "model": config.MODEL,
        "messages": messages
    }
    for attempt in range(3):
        try:
            resp = requests.post(config.API_URL, headers=headers, json=data, timeout=60)
            break
        except requests.exceptions.Timeout:
            if attempt == 2:
                return "请求超时了，请检查网络或稍后再试。"
            time.sleep(2)
        except requests.exceptions.ConnectionError:
            if attempt == 2:
                return "连不上服务器，请检查网络连接。"
            time.sleep(2)
        except Exception as e:
            if attempt == 2:
                return f"请求出错：{e}"
            time.sleep(2)
    result = resp.json()
    if "choices" not in result:
        return "出错啦：" + str(result)
    return result["choices"][0]["message"]["content"]

def clean_markdown(text):
    import re
    if not isinstance(text, str):
        return text
    # 先正常处理成对粗体(渲染成真粗体,交给 Markdown)
    # 只清理"残缺"的裸符号:不成对的星号、孤立井号、LaTeX 残留
    text = text.replace("\\rightarrow", "->").replace("\\Rightarrow", "=>")
    # 去掉行首单独出现的 #(无内容跟随的孤立标题符)
    text = re.sub(r"(?m)^#{1,6}\s*$", "", text)
    # 清理不成对的孤立星号:先统计,把落单的 * 去掉(成对保留给 Markdown 渲染)
    # 简化:去掉被文本包围的单个 * (非成对)
    text = re.sub(r"(?<!\*)\*(?!\*)", "", text)
    return text

def save_history():
    with open("history.json", "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def load_history():
    try:
        with open("history.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        import shutil,time
        backup = f"history.json.bak-{int(time.time())}"
        shutil.copy("history.json", backup)
        return[]
MEMORY_FILE = "memory.json"
memory = []

def load_memory():
    global memory
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            memory = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        memory = []

def save_memory():
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)

def extract_facts(recent):
    extract_prompt = (
        "你是记忆提取器。从对话中提取值得长期记住的用户关键信息"
        "(名字、身份、正在做的事、项目、偏好、重要事件等)。"
        "只输出 JSON 数组,每项一个字符串事实;没有新事实就输出 []。"
        "不要输出任何其他文字。"
    )
    headers = {
        "Authorization": f"Bearer {config.API_KEY}",
        "Content-Type": "application/json"
    }
    msgs = [{"role": "system", "content": extract_prompt}] + recent
    data = {"model": config.MODEL, "messages": msgs}
    resp = requests.post(config.API_URL, headers=headers, json=data)
    result = resp.json()
    if "choices" not in result:
        return []
    content = result["choices"][0]["message"]["content"].strip()
    try:
        facts = json.loads(content)
        return facts if isinstance(facts, list) else []
    except json.JSONDecodeError:
        return []

def update_memory():
    try:
        recent = history[-4:]
        if len(recent) < 2:
            return
        new_facts = extract_facts(recent)
        added = False
        for fact in new_facts:
            fact = str(fact).strip()
            if fact and fact not in memory:
                memory.append(fact)
                added = True
        if added:
            save_memory()
    except Exception:
        pass

def main(page: ft.Page):
    page.title = "AI聊天助手"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = ft.Colors.GREY_100
    page.padding = 0

    top = ft.Container(
        content = ft.Row(
            [   ft.Icon(ft.Icons.CHAT,color = ft.Colors.WHITE),
                ft.Text("AI聊天助手", size=24, weight=ft.FontWeight.BOLD)
                ],
                 alignment = ft.MainAxisAlignment.CENTER,
                 spacing = 8,
        ),
        bgcolor = ft.Colors.BLUE_500,
        padding = 15,
    )

    message = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True,auto_scroll=True,margin = 15)
    input_box = ft.TextField(hint_text="输入消息...", expand = True,multiline = True,min_lines = 1,max_lines=5,
                             shift_enter = True,border_radius = 24,filled = True,fill_color = ft.Colors.WHITE,
                             border_color =  ft.Colors.BLUE_200,focused_border_color = ft.Colors.BLUE_600,
                             content_padding = ft.Padding(15,10,15,10))

    picker = ft.FilePicker()

    async def pick_image(e):
        files = await picker.pick_files(
            dialog_title="选择聊天截图",
            file_type=ft.FilePickerFileType.IMAGE,
            with_data=True,
            allow_multiple=False,
        )
        if not files:
            return
        image_bytes = files[0].bytes
        import base64, io
        from PIL import Image
        try:
            img = Image.open(io.BytesIO(image_bytes))
            img.thumbnail((1024, 1024))
            buf = io.BytesIO()
            img.convert("RGB").save(buf, format="JPEG", quality=80)
            image_bytes = buf.getvalue()
        except Exception:
            pass
        b64 = base64.b64encode(image_bytes).decode()
        data_url = f"data:image/jpeg;base64,{b64}"
        text = input_box.value.strip()
        input_box.value = ""
        if text:
            full_msg = f"[图片] {text}"
        else:
            full_msg = "[图片]"
        add_msg(full_msg, True)
        history.append({"role": "user", "content": [
            {"type": "text", "text": text or "请看这张图"},
            {"type": "image_url", "image_url": {"url": data_url}},
        ]})
        save_history()

        wait_msg = add_msg("正在看图", False)
        page.update()
        anim_stop = False

        async def img_anim():
            frames = ["正在看图", "正在看图.", "正在看图..", "正在看图..."]
            i = 0
            while not anim_stop:
                wait_msg.content = ft.Text(frames[i % 4])
                page.update()
                await asyncio.sleep(0.4)
                i += 1

        page.run_task(img_anim)

        async def do_vision():
            nonlocal anim_stop
            try:
                reply = chat_with_ai(history)
                anim_stop = True
                history.append({"role": "assistant", "content": reply})
                save_history()
                update_memory()
                wait_msg.content = ft.Markdown(clean_markdown(reply), selectable = True, extension_set = ft.MarkdownExtensionSet.GITHUB_WEB, fit_content = True)
            except Exception as ex:
                anim_stop = True
                wait_msg.content = ft.Text(f"图片处理失败：{ex}")
            page.update()

        page.run_task(do_vision)

    img_btn = ft.IconButton(
        icon=ft.Icons.IMAGE,
        icon_size=20,
        icon_color=ft.Colors.BLUE_600,
        tooltip="发送图片",
        on_click=pick_image,
    )
    msg_boxes = []
    resize_busy = False

    def bubble_width():
        w = page.width or 900
        return max(300, int(w * 0.7))

    async def resize_bubbles(e=None):
        nonlocal resize_busy
        if resize_busy:
            return
        resize_busy = True
        await asyncio.sleep(0.15)
        resize_busy = False
        new_w = bubble_width()
        changed = False
        for b in msg_boxes:
            if b.width != new_w:
                b.width = new_w
                changed = True
        if changed:
            page.update()

    page.on_resize = resize_bubbles

    def add_msg(text, is_me):
        msg = ft.Container(
            content=(ft.Text(text, color=ft.Colors.WHITE, selectable = True) if is_me
                     else ft.Markdown(clean_markdown(text), selectable = True, extension_set = ft.MarkdownExtensionSet.GITHUB_WEB, fit_content = True)),
            bgcolor=ft.Colors.BLUE_600 if is_me else ft.Colors.WHITE,
            padding=12,
            border_radius=18,
            width=bubble_width(),
            shadow=ft.BoxShadow(blur_radius=4, color=ft.Colors.BLACK12),
            alignment=ft.Alignment.CENTER_RIGHT if is_me else ft.Alignment.CENTER_LEFT,
        )
        msg_boxes.append(msg)

        async def copy_text(t):
            clipboard = ft.Clipboard()
            await clipboard.set(t)
            page.overlay.append(ft.SnackBar(content=ft.Text("已复制"), open=True))
            page.update()

        wrapper = ft.GestureDetector(
                content=msg,
                on_double_tap=lambda e, t=text: copy_text(t),
            )

        label = ft.Text(
            "我" if is_me else "AI",
            size=11,
            color=ft.Colors.BLUE_600 if is_me else ft.Colors.GREY_500,
            weight=ft.FontWeight.BOLD,
        )
        bubble_row = ft.Row(
            [label, wrapper] if not is_me else [wrapper, label],
            alignment=ft.MainAxisAlignment.START if not is_me else ft.MainAxisAlignment.END,
            spacing=6,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        message.controls.append(bubble_row)
        page.update()
        return msg
    global history
    history =load_history()
    if not history:
        message.controls.append(
            ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(ft.Icons.CHAT, size=64, color=ft.Colors.BLUE_200),
                        ft.Text("你好，我是狗头军师", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_700),
                        ft.Text("双击消息可复制，Enter发送，Shift+Enter换行", size=13, color=ft.Colors.GREY_500),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=12,
                ),
                alignment=ft.Alignment.CENTER,
                expand=True,
            )
        )
        page.update()
    for item in history:
        c = item["content"]
        if isinstance(c, list):
            c = "[图片]"
        add_msg(c, item["role"] == "user")

    def send_message(e):
        text = input_box.value
        if not text.strip():
            return
        add_msg(text, True)
        input_box.value = ""
        history.append({"role": "user", "content": text})
        save_history()


        wait_msg = add_msg("正在思考", False)
        page.update()

        anim_stop = False

        async def thinking_animation():
            frames = ["正在思考", "正在思考.", "正在思考..", "正在思考..."]
            i = 0
            while not anim_stop:
                wait_msg.content = ft.Text(frames[i % 4])
                page.update()
                await asyncio.sleep(0.4)
                i += 1

        page.run_task(thinking_animation)

        async def do_ai():
            nonlocal anim_stop
            reply = chat_with_ai(history)
            anim_stop = True
            history.append({"role": "assistant", "content": reply})
            save_history()
            update_memory()
            wait_msg.content = ft.Markdown(clean_markdown(reply), selectable = True, extension_set = ft.MarkdownExtensionSet.GITHUB_WEB, fit_content = True)
            page.update()

        page.run_task(do_ai)
    input_box.on_submit = send_message
    send_btn = ft.IconButton(
        icon = ft.Icons.SEND,
        icon_size = 22,
        icon_color = ft.Colors.WHITE,
        width = 46,
        height = 46,
        style = ft.ButtonStyle(
            bgcolor = ft.Colors.BLUE_600,
            shape = ft.RoundedRectangleBorder(radius = 23),
        ),
        tooltip = "发送",
        on_click = send_message,
    )
    input_row = ft.Container(
        content = ft.Row([img_btn, input_box, send_btn], spacing = 8),
        padding = ft.Padding(15,12,15,12),
        bgcolor = ft.Colors.GREY_50,
        border_radius = ft.BorderRadius(top_left = 20,top_right = 20,bottom_left = 0,bottom_right = 0,),
    )
    page.add(top, message, input_row)

ft.run(main)