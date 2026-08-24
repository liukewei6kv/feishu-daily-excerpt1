#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
云端书摘推送脚本（webhook 版）- 《从零开始做运营》60天计划
============================================================
适用场景：部署到云端（GitHub Actions / 云服务器 / PythonAnywhere 等），
不依赖本地电脑，关机也能定时推送。

原理：
1. 使用飞书群聊「自定义机器人」的 webhook URL 发送消息（无需应用凭据）
2. 书摘全文（从零开始做运营_60天书摘.md）与进度（书摘进度.json）与本脚本同目录
3. 每天定时运行一次：读取进度 → 提取当天书摘 → POST 到 webhook → 更新进度

使用方式：
    export FEISHU_WEBHOOK_URL="https://open.feishu.cn/open-apis/bot/v2/hook/xxxx"
    python cloud_send_excerpt.py

或直接修改下方 WEBHOOK_URL 常量。

依赖：仅标准库（urllib），无需 pip install。
"""
import json
import os
import re
import subprocess
import sys
import time
import urllib.request

# ====== 配置 ======
WEBHOOK_URL = os.environ.get("FEISHU_WEBHOOK_URL", "YOUR_WEBHOOK_URL_HERE")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROGRESS_FILE = os.path.join(BASE_DIR, "书摘进度.json")
EXCERPT_FILE = os.path.join(BASE_DIR, "从零开始做运营_60天书摘.md")
MAX_RETRY = 3
RETRY_DELAY = 5  # 秒


def send_to_webhook(text: str) -> bool:
    """发送文本消息到飞书 webhook，带重试。返回是否成功。"""
    payload = json.dumps({"msg_type": "text", "content": {"text": text}}, ensure_ascii=False).encode("utf-8")
    for attempt in range(1, MAX_RETRY + 1):
        try:
            req = urllib.request.Request(
                WEBHOOK_URL,
                data=payload,
                headers={"Content-Type": "application/json; charset=utf-8"},
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode("utf-8"))
            if result.get("code") == 0 or result.get("StatusCode") == 0:
                print(f"[成功] 第 {attempt}/{MAX_RETRY} 次尝试发送成功")
                return True
            print(f"[失败] 第 {attempt}/{MAX_RETRY} 次尝试: {result}")
        except Exception as e:
            print(f"[失败] 第 {attempt}/{MAX_RETRY} 次尝试异常: {e}")
        if attempt < MAX_RETRY:
            print(f"{RETRY_DELAY} 秒后重试...")
            time.sleep(RETRY_DELAY)
    return False


def main():
    if not WEBHOOK_URL or WEBHOOK_URL == "YOUR_WEBHOOK_URL_HERE":
        print("[错误] 未配置 FEISHU_WEBHOOK_URL 环境变量，请先配置 webhook 地址")
        sys.exit(1)

    # 读取进度
    with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
        progress = json.load(f)

    last_sent = progress.get("lastSentDay", 0)
    total = progress.get("totalDays", 60)
    day = last_sent + 1

    if day > total:
        print("[完成] 60天书摘已全部发送完毕")
        send_to_webhook("【从零开始做运营】60天书摘已全部发送完毕，感谢坚持！")
        sys.exit(0)

    print(f"准备发送第 {day}/{total} 天书摘")

    # 读取书摘内容
    with open(EXCERPT_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = rf"## Day {day}\n(.*?)(?=\n\n## Day |\Z)"
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        print(f"[错误] 未找到 Day {day} 的书摘内容")
        sys.exit(1)

    excerpt = match.group(1).strip()
    message = f"【从零开始做运营】第 {day}/{total} 天书摘\n\n{excerpt}\n\n—— 张亮《从零开始做运营》"
    if day == total:
        message += "\n\n🎉 今天是最后一天，60天书摘计划圆满完成！"

    # 发送（带重试）
    if send_to_webhook(message):
        # 更新进度
        progress["lastSentDay"] = day
        with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
            json.dump(progress, f, ensure_ascii=False, indent=2)
        print(f"进度已更新: lastSentDay = {day}")

        # GitHub Actions 环境下自动提交进度更新
        if os.environ.get("GITHUB_ACTIONS") == "true":
            try:
                subprocess.run(["git", "add", "书摘进度.json"], check=False)
                result = subprocess.run(
                    ["git", "diff", "--cached", "--quiet"],
                    capture_output=True,
                )
                if result.returncode != 0:
                    subprocess.run(
                        ["git", "commit", "-m", f"Update excerpt progress: Day {day} [skip ci]"],
                        check=False,
                    )
                    subprocess.run(["git", "push"], check=False)
                    print(f"[GitHub Actions] 进度已提交到仓库")
            except Exception as e:
                print(f"[GitHub Actions] 提交进度时出错（非致命）: {e}")
    else:
        print("[错误] 重试后仍发送失败，进度未更新（下次运行会重发同一天）")
        sys.exit(1)


if __name__ == "__main__":
    main()
