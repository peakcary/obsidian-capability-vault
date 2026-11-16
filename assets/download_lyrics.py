#!/usr/bin/env python3
"""批量下载真实带时间轴的 LRC，使用 Python 标准库。

用法：python3 download_lyrics.py [音乐文件夹] [--output 歌词文件夹]
默认来源：网易云、QQ、酷狗；可用 --lrclib、--musixmatch KEY 增加来源。
"""

import argparse
import base64
import html
import json
import os
import re
import socket
import sys
import tempfile
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

DEFAULT_DIR = "/Users/peakom/Downloads/热门歌手成名代表作"
DELAY = 0.4
TIMEOUT = 12
MAX_RETRY = 2
MAX_RESPONSE = 2 * 1024 * 1024
AUDIO_EXT = (".wav", ".mp3", ".flac", ".m4a", ".ape", ".ogg", ".wma", ".aac", ".aiff")
STAMP = re.compile(r"\[\d{1,3}:[0-5]\d(?:[.:]\d{1,3})?\]")
TAGS = re.compile(r"\[[^\]\r\n]*\]")
_proxy_opener = None
_musixmatch_key = None
_last_request = 0.0


def setup_proxy(host_port):
    """接受 HOST:PORT 或完整 HTTP(S) 代理地址，不打印代理凭据。"""
    global _proxy_opener
    address = host_port if "://" in host_port else "http://" + host_port
    parsed = urllib.parse.urlsplit(address)
    try:
        port = parsed.port
    except ValueError as exc:
        raise ValueError("代理端口无效") from exc
    if (parsed.scheme not in ("http", "https") or not parsed.hostname or not port
            or parsed.path not in ("", "/") or parsed.query or parsed.fragment):
        raise ValueError("代理格式应为 HOST:PORT 或 http://HOST:PORT")
    _proxy_opener = urllib.request.build_opener(
        urllib.request.ProxyHandler({"http": address, "https": address}))


def http_get(url, headers=None, timeout=TIMEOUT):
    """统一限速和有限重试；错误不包含带 API key 的完整请求地址。"""
    global _last_request
    request_headers = {"User-Agent": "Mozilla/5.0 LyricsDownloader/2.0"}
    request_headers.update(headers or {})
    request = urllib.request.Request(url, headers=request_headers)
    opener = _proxy_opener or urllib.request.build_opener()
    for attempt in range(MAX_RETRY):
        pause = DELAY - (time.monotonic() - _last_request)
        if pause > 0:
            time.sleep(pause)
        _last_request = time.monotonic()
        try:
            with opener.open(request, timeout=timeout) as response:
                data = response.read(MAX_RESPONSE + 1)
            if len(data) > MAX_RESPONSE:
                raise ValueError("接口响应超过 2 MiB，已拒绝")
            return data.decode("utf-8-sig")
        except urllib.error.HTTPError as exc:
            status = exc.code
            exc.close()
            if attempt + 1 == MAX_RETRY or (status != 429 and not 500 <= status < 600):
                raise RuntimeError(f"接口返回 HTTP {status}") from None
            wait = 20 if status == 429 else 2
            print(f"\n  HTTP {status}，等待 {wait} 秒后重试", flush=True)
            time.sleep(wait)
        except (urllib.error.URLError, TimeoutError, socket.timeout) as exc:
            if attempt + 1 == MAX_RETRY:
                reason = exc.reason if isinstance(exc, urllib.error.URLError) else exc
                raise RuntimeError(f"网络或 TLS 请求失败（{type(reason).__name__}）") from None
            time.sleep(2)


def get_json(url, params=None, headers=None):
    if params:
        url += "?" + urllib.parse.urlencode(params)
    return json.loads(http_get(url, headers))


def parse_filename(filename):
    """保留 Live、DJ、粤语等版本信息，避免错配另一录音版本。"""
    name = Path(filename).name
    if Path(name).suffix.lower() in AUDIO_EXT:
        name = name[:-len(Path(name).suffix)]
    for separator in ("-", "－", "—"):
        if separator in name:
            artist, title = name.split(separator, 1)
            return artist.strip(), title.strip()
    if "《" in name and name.endswith("》"):
        artist, title = name.split("《", 1)
        return artist.strip(), title[:-1].strip()
    if " " in name:
        artist, title = name.split(" ", 1)
        if re.search(r"[\u3400-\u9fff]", title):
            return artist.strip(), title.strip()
    return "", name.strip()


def normalize(text):
    return "".join(c for c in unicodedata.normalize("NFKC", text).casefold() if c.isalnum())


def matches(artist, title, candidate_title, candidate_artists):
    if not normalize(title) or normalize(title) != normalize(candidate_title):
        return False
    if not artist:
        return True
    wanted = [normalize(p) for p in re.split(r"[&＆、/]", artist) if normalize(p)]
    available = {normalize(p) for name in candidate_artists
                 for p in re.split(r"[&＆、/]", name) if normalize(p)}
    return bool(wanted) and all(name in available for name in wanted)


def clean_lrc(text):
    """只接受时间戳后有文字的行；不把纯文本或元数据伪装成 LRC。"""
    if not isinstance(text, str):
        return None
    lines = [line.strip() for line in html.unescape(text).lstrip("\ufeff").splitlines() if line.strip()]
    if not any(STAMP.match(line) and TAGS.sub("", line).strip() for line in lines):
        return None
    return "\n".join(lines) + "\n"


def decode_lrc(text):
    """兼容接口返回的明文、HTML 实体和 Base64。"""
    plain = clean_lrc(text)
    if plain:
        return plain
    if not isinstance(text, str):
        return None
    try:
        return clean_lrc(base64.b64decode(text, validate=True).decode("utf-8-sig"))
    except (ValueError, UnicodeError):
        return None


def fetch_netease(artist, title):
    headers = {"Referer": "https://music.163.com/"}
    data = get_json("https://music.163.com/api/search/get",
                    {"s": f"{artist} {title}".strip(), "type": 1, "limit": 5}, headers)
    for song in data.get("result", {}).get("songs", []):
        names = [a.get("name", "") for a in song.get("artists", song.get("ar", []))]
        if not matches(artist, title, song.get("name", ""), names):
            continue
        result = get_json("https://music.163.com/api/song/lyric",
                          {"id": song["id"], "lv": 1, "kv": 1, "tv": -1}, headers)
        lrc = clean_lrc(result.get("lrc", {}).get("lyric"))
        if lrc:
            return lrc
    return None


def fetch_qq(artist, title):
    headers = {"Referer": "https://y.qq.com/"}
    data = get_json("https://c.y.qq.com/soso/fcgi-bin/client_search_cp",
                    {"w": f"{artist} {title}".strip(), "format": "json", "n": 5,
                     "p": 1, "cr": 1, "g_tk": 5381}, headers)
    for song in data.get("data", {}).get("song", {}).get("list", []):
        if not matches(artist, title, song.get("songname", ""),
                       [a.get("name", "") for a in song.get("singer", [])]):
            continue
        result = get_json("https://c.y.qq.com/lyric/fcgi-bin/fcg_query_lyric_new.fcg",
                          {"songmid": song["songmid"], "format": "json", "nobase64": 1}, headers)
        lrc = decode_lrc(result.get("lyric"))
        if lrc:
            return lrc
    return None


def fetch_kugou(artist, title):
    data = get_json("https://mobileservice.kugou.com/api/v3/lyric/search",
                    {"keyword": f"{artist} {title}".strip(), "version": 9108,
                     "highlight": 0, "plat": 0, "pagesize": 5, "area_code": 1, "page": 1})
    for song in data.get("data", {}).get("info", []):
        singer, name = parse_filename(song.get("filename", ""))
        if not matches(artist, title, name, [song.get("singername") or singer]):
            continue
        result = get_json("https://lyrics.kugou.com/search",
                          {"ver": 1, "man": "yes", "client": "pc", "hash": song["hash"]})
        for candidate in result.get("candidates", []):
            content = get_json("https://lyrics.kugou.com/download",
                               {"ver": 1, "client": "pc", "id": candidate["id"],
                                "accesskey": candidate["accesskey"], "fmt": "lrc", "charset": "utf8"})
            lrc = decode_lrc(content.get("content"))
            if lrc:
                return lrc
    return None


def fetch_lrclib(artist, title):
    params = {"track_name": title}
    if artist:
        params["artist_name"] = artist
    data = get_json("https://lrclib.net/api/search", params, {"Accept": "application/json"})
    for item in data:
        if matches(artist, title, item.get("trackName", ""), [item.get("artistName", "")]):
            lrc = clean_lrc(item.get("syncedLyrics"))
            if lrc:
                return lrc
    return None


def fetch_musixmatch(artist, title):
    if not _musixmatch_key:
        return None
    data = get_json("https://api.musixmatch.com/ws/1.1/matcher.subtitle.get",
                    {"q_artist": artist, "q_track": title, "apikey": _musixmatch_key,
                     "format": "json", "subtitle_format": "lrc"})
    message = data.get("message", {})
    status = message.get("header", {}).get("status_code")
    if status != 200:
        raise RuntimeError(f"Musixmatch 返回状态 {status}，请检查密钥、字幕权限和配额")
    subtitle = message.get("body", {}).get("subtitle", {})
    if subtitle.get("restricted"):
        return None
    # 没有真实字幕就回退其他源，不对纯文本编造时间轴。
    return clean_lrc(subtitle.get("subtitle_body"))


def build_sources(use_cn, use_lrclib, musixmatch_key):
    global _musixmatch_key
    _musixmatch_key = musixmatch_key
    sources = []
    if use_cn:
        sources.extend([("网易云", fetch_netease), ("QQ音乐", fetch_qq), ("酷狗", fetch_kugou)])
    if use_lrclib:
        sources.append(("LRCLIB", fetch_lrclib))
    if musixmatch_key:
        sources.append(("Musixmatch", fetch_musixmatch))
    return sources


def save_lrc(path, text):
    """临时文件写完后提交，重复执行和并发时均不覆盖已有文件。"""
    path = Path(path)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n",
                                         dir=path.parent, prefix=".lyrics-", suffix=".tmp", delete=False) as f:
            temporary = Path(f.name)
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        # shortcut: 提交需要硬链接，支持 FAT/exFAT 或部分网络盘时需替换提交方式。
        os.link(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def safe_error(exc):
    text = str(exc)
    return text.replace(_musixmatch_key, "[已隐藏密钥]") if _musixmatch_key else text


def download_one(filepath, sources, output_dir=None):
    filepath = Path(filepath)
    artist, title = parse_filename(filepath.name)
    lrc_path = (Path(output_dir) if output_dir is not None else filepath.parent) / (filepath.stem + ".lrc")
    if os.path.lexists(lrc_path):
        return "skip", None
    if not title:
        print("\n  歌名为空，未发送请求")
        return "fail", None
    for src_name, fetcher in sources:
        try:
            lrc = clean_lrc(fetcher(artist, title))
        except Exception as exc:
            print(f"\n  {src_name}：{safe_error(exc)}", flush=True)
            continue
        if not lrc:
            continue
        try:
            save_lrc(lrc_path, lrc)
        except FileExistsError:
            return "skip", None
        except OSError as exc:
            print(f"\n  保存失败：{safe_error(exc)}", flush=True)
            return "fail", None
        return "ok", src_name
    return "fail", None


def write_failures(output_dir, failures):
    path = Path(output_dir) / "_lyrics_failed.txt"
    if not failures and not path.exists():
        return
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=output_dir,
                                         prefix=".lyrics-report-", delete=False) as f:
            temporary = Path(f.name)
            f.write("\n".join(failures) + ("\n" if failures else ""))
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description="批量下载真实带时间轴的 LRC 歌词")
    parser.add_argument("dir", nargs="?", default=DEFAULT_DIR, help="音乐文件夹路径，只扫描当前层")
    parser.add_argument("--output", metavar="DIR", help="指定已有的歌词保存文件夹，默认保存到音频旁")
    parser.add_argument("--lrclib", action="store_true", help="启用 LRCLIB；是否需要代理取决于当前网络")
    parser.add_argument("--musixmatch", metavar="KEY", help="启用 Musixmatch 真实字幕，需要相应 API 权限")
    parser.add_argument("--no-cn", action="store_true", help="禁用网易云、QQ、酷狗")
    parser.add_argument("--proxy", metavar="HOST:PORT", help="HTTP(S) 代理地址，如 127.0.0.1:7890")
    args = parser.parse_args(argv)
    source_dir = Path(args.dir).expanduser().resolve()
    output_dir = Path(args.output).expanduser().resolve() if args.output else source_dir
    if not source_dir.is_dir():
        parser.error("音乐文件夹不存在或无法访问")
    if not output_dir.is_dir():
        parser.error("歌词保存文件夹不存在或无法访问")
    if args.proxy:
        try:
            setup_proxy(args.proxy)
        except ValueError as exc:
            parser.error(str(exc))
        print("已启用指定代理")
    sources = build_sources(not args.no_cn, args.lrclib, args.musixmatch)
    if not sources:
        parser.error("未启用任何数据源，请使用 --lrclib 或 --musixmatch")
    try:
        files = sorted(p for p in source_dir.iterdir() if p.is_file() and not p.is_symlink()
                       and p.suffix.lower() in AUDIO_EXT)
    except OSError as exc:
        print(f"无法读取音乐文件夹：{safe_error(exc)}", file=sys.stderr)
        return 1
    if not files:
        print("未找到支持的音频文件")
        return 0
    print("数据源: " + " / ".join(name for name, _ in sources))
    print(f"共 {len(files)} 首，歌词保存到: {output_dir}\n")
    counts = {"ok": 0, "skip": 0, "fail": 0}
    failures = []
    interrupted = False
    try:
        for index, filepath in enumerate(files, 1):
            print(f"[{index}/{len(files)}] {filepath.name}", end=" ... ", flush=True)
            status, source = download_one(filepath, sources, output_dir)
            counts[status] += 1
            if status == "fail":
                failures.append(filepath.name)
                print("失败（未取得匹配的有效 LRC，或保存失败）")
            elif status == "skip":
                print("跳过（目标已存在）")
            else:
                print(f"OK ({source})")
    except KeyboardInterrupt:
        interrupted = True
        print("\n已中断；已保存的文件保留，重跑会自动跳过。")
    pending = len(files) - sum(counts.values())
    print(f"\n完成: 成功 {counts['ok']} | 跳过 {counts['skip']} | 失败 {counts['fail']} | 未处理 {pending} | 共 {len(files)}")
    try:
        write_failures(output_dir, failures)
    except OSError as exc:
        print(f"失败列表保存失败：{safe_error(exc)}", file=sys.stderr)
        return 130 if interrupted else 1
    if failures:
        print(f"失败列表已保存: {output_dir / '_lyrics_failed.txt'}")
    return 130 if interrupted else (1 if failures else 0)


if __name__ == "__main__":
    sys.exit(main())
