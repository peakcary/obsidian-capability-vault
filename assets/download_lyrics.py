#!/usr/bin/env python3
"""
批量下载歌词脚本 - 多源互补
支持: 网易云 / QQ音乐 / 酷狗音乐
用法: python3 download_lyrics.py [音乐文件夹路径]
"""

import os
import re
import sys
import time
import json
import random
import urllib.request
import urllib.parse
import hashlib
from pathlib import Path

# ========== 配置 ==========
DEFAULT_DIR = "/Users/peakom/Downloads/热门歌手成名代表作"
DELAY = 0.4          # 请求间隔（秒）
TIMEOUT = 12         # 单请求超时
MAX_RETRY = 2        # 单源重试次数
AUDIO_EXT = (".wav", ".mp3", ".flac", ".m4a", ".ape", ".ogg", ".wma")

UA_LIST = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
]


# ========== 工具函数 ==========

def rand_ua():
    return random.choice(UA_LIST)


def http_get(url, headers=None, timeout=TIMEOUT):
    """发起 GET 请求，返回响应文本"""
    h = {"User-Agent": rand_ua()}
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, headers=h)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def http_post(url, data, headers=None, timeout=TIMEOUT):
    """发起 POST 请求，返回响应文本"""
    h = {
        "User-Agent": rand_ua(),
        "Content-Type": "application/x-www-form-urlencoded",
    }
    if headers:
        h.update(headers)
    if isinstance(data, dict):
        data = urllib.parse.urlencode(data).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=h)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def parse_filename(filename):
    """从文件名解析歌手和歌名"""
    name = Path(filename).stem
    # 去掉常见噪声后缀
    name = re.sub(r"\s*\(.*?\)\s*", "", name)       # 去括号注释 如 (live) (dj版)
    name = re.sub(r"\s*\[.*?\]\s*", "", name)
    # 厸手-歌名 分割
    if "-" in name:
        parts = name.split("-", 1)
        return parts[0].strip(), parts[1].strip()
    return "", name.strip()


def clean_lrc(text):
    """简单清洗 LRC：去空行、去 ID 标签冗余"""
    if not text:
        return None
    lines = []
    for line in text.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        lines.append(line)
    return "\n".join(lines) if lines else None


# ========== 数据源 1: 网易云音乐 ==========

def netease_search(artist, title):
    keyword = f"{artist} {title}".strip()
    encoded = urllib.parse.quote(keyword)
    url = f"https://music.163.com/api/search/get?s={encoded}&type=1&limit=5"
    headers = {"Referer": "https://music.163.com/"}
    try:
        data = json.loads(http_get(url, headers))
        songs = data.get("result", {}).get("songs", [])
        if not songs:
            return None
        return songs[0]["id"]
    except Exception:
        return None


def netease_lyric(song_id):
    url = f"https://music.163.com/api/song/lyric?id={song_id}&lv=1&kv=1&tv=-1"
    headers = {"Referer": "https://music.163.com/"}
    try:
        data = json.loads(http_get(url, headers))
        lrc = data.get("lrc", {}).get("lyric", "")
        return clean_lrc(lrc)
    except Exception:
        return None


def fetch_netease(artist, title):
    song_id = netease_search(artist, title)
    if not song_id:
        return None
    return netease_lyric(song_id)


# ========== 数据源 2: QQ音乐 ==========

def qq_search(artist, title):
    keyword = f"{artist} {title}".strip()
    encoded = urllib.parse.quote(keyword)
    url = (
        f"https://c.y.qq.com/soso/fcgi-bin/client_search_cp?"
        f"w={encoded}&format=json&n=5&p=1&cr=1&g_tk=5381"
    )
    headers = {"Referer": "https://y.qq.com/"}
    try:
        data = json.loads(http_get(url, headers))
        songs = data.get("data", {}).get("song", {}).get("list", [])
        if not songs:
            return None
        return songs[0]["songmid"]
    except Exception:
        return None


def qq_lyric(songmid):
    url = f"https://c.y.qq.com/lyric/fcgi-bin/fcg_query_lyric_new.fcg?songmid={songmid}&format=json&nobase64=1"
    headers = {"Referer": "https://y.qq.com/"}
    try:
        data = json.loads(http_get(url, headers))
        # QQ 返回的歌词是 base64 编码
        import base64
        lrc_b64 = data.get("lyric", "")
        if not lrc_b64:
            return None
        lrc = base64.b64decode(lrc_b64).decode("utf-8", errors="ignore")
        return clean_lrc(lrc)
    except Exception:
        return None


def fetch_qq(artist, title):
    songmid = qq_search(artist, title)
    if not songmid:
        return None
    return qq_lyric(songmid)


# ========== 数据源 3: 酷狗音乐 ==========

def kugou_search(artist, title):
    keyword = f"{artist} {title}".strip()
    encoded = urllib.parse.quote(keyword)
    url = (
        f"http://mobilecdn.kugou.com/api/v3/search/song?"
        f"keyword={encoded}&page=1&pagesize=5&format=json"
    )
    try:
        data = json.loads(http_get(url))
        songs = data.get("data", {}).get("info", [])
        if not songs:
            return None
        # 酷狗需要 hash 来取歌词
        return songs[0]["hash"]
    except Exception:
        return None


def kugou_lyric(hash_str):
    url = f"http://krcs.kugou.com/lyric?id={hash_str}&accesschain=&client=pc&format=lrc"
    try:
        data = json.loads(http_get(url))
        content = data.get("content", "")
        if not content:
            return None
        import base64
        lrc = base64.b64decode(content).decode("utf-8", errors="ignore")
        return clean_lrc(lrc)
    except Exception:
        return None


def fetch_kugou(artist, title):
    hash_str = kugou_search(artist, title)
    if not hash_str:
        return None
    return kugou_lyric(hash_str)


# ========== 主流程 ==========

SOURCES = [
    ("网易云", fetch_netease),
    ("QQ音乐", fetch_qq),
    ("酷狗", fetch_kugou),
]


def download_one(filepath):
    """下载单首歌歌词，多源尝试，返回 (状态, 来源)"""
    filename = os.path.basename(filepath)
    artist, title = parse_filename(filename)
    lrc_path = str(Path(filepath).with_suffix(".lrc"))

    for src_name, fetcher in SOURCES:
        for attempt in range(MAX_RETRY):
            try:
                lrc = fetcher(artist, title)
                if lrc and len(lrc) > 20:
                    with open(lrc_path, "w", encoding="utf-8") as f:
                        f.write(lrc)
                    return "ok", src_name
            except Exception:
                pass
            time.sleep(DELAY)
    return "fail", None


def main():
    music_dir = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DIR

    if not os.path.isdir(music_dir):
        print(f"错误: 文件夹不存在: {music_dir}")
        sys.exit(1)

    files = sorted(
        f for f in os.listdir(music_dir)
        if f.lower().endswith(AUDIO_EXT)
    )
    total = len(files)
    if total == 0:
        print("未找到音频文件")
        sys.exit(0)

    success, skip, fail = 0, 0, 0
    fail_list = []

    print(f"共 {total} 首歌曲，开始下载歌词...\n")

    for i, filename in enumerate(files, 1):
        filepath = os.path.join(music_dir, filename)
        artist, title = parse_filename(filename)
        lrc_path = os.path.join(music_dir, Path(filename).stem + ".lrc")

        # 已存在跳过
        if os.path.exists(lrc_path):
            print(f"[{i}/{total}] 跳过(已存在): {artist} - {title}")
            skip += 1
            continue

        print(f"[{i}/{total}] {artist} - {title}", end=" ... ", flush=True)
        status, src = download_one(filepath)

        if status == "ok":
            print(f"OK ({src})")
            success += 1
        else:
            print("失败")
            fail += 1
            fail_list.append(f"{artist} - {title}")

        time.sleep(DELAY)

    # 汇总
    print(f"\n{'='*40}")
    print(f"完成: 成功 {success} | 跳过 {skip} | 失败 {fail} | 共 {total}")

    if fail_list:
        print(f"\n失败列表 ({len(fail_list)} 首):")
        for name in fail_list:
            print(f"  - {name}")

        # 保存失败列表
        fail_path = os.path.join(music_dir, "_lyrics_failed.txt")
        with open(fail_path, "w", encoding="utf-8") as f:
            f.write("\n".join(fail_list))
        print(f"\n失败列表已保存: {fail_path}")


if __name__ == "__main__":
    main()
