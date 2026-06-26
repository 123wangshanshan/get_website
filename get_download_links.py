#!/usr/bin/env python3
"""Fetch a webpage and extract download links into a text file."""

import argparse
import re
import ssl
import sys
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen


DOWNLOAD_EXTENSIONS = {
    ".zip",
    ".rar",
    ".7z",
    ".tar",
    ".gz",
    ".tgz",
    ".bz2",
    ".exe",
    ".msi",
    ".dmg",
    ".iso",
    ".pdf",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".ppt",
    ".pptx",
    ".mp3",
    ".mp4",
    ".m4a",
    ".avi",
    ".mkv",
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".svg",
    ".txt",
    ".csv",
}


class LinkExtractor(HTMLParser):
    def __init__(self, base_url):
        super().__init__()
        self.base_url = base_url
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() != "a":
            return
        for name, value in attrs:
            if name.lower() == "href" and value:
                self.links.append(value)


def is_download_link(url):
    try:
        parsed = urlparse(url)
    except Exception:
        return False
    path = parsed.path.lower()
    if any(path.endswith(ext) for ext in DOWNLOAD_EXTENSIONS):
        return True
    if "download" in path or "download" in parsed.query.lower():
        return True
    return False


def fetch_html(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    request = Request(url, headers=headers)
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    with urlopen(request, context=context) as response:
        charset = response.headers.get_content_charset(failobj="utf-8")
        return response.read().decode(charset, errors="replace")


def extract_download_links(url):
    html = fetch_html(url)
    parser = LinkExtractor(url)
    parser.feed(html)
    absolute_links = []
    for link in parser.links:
        absolute = urljoin(url, link.strip())
        if is_download_link(absolute):
            absolute_links.append(absolute)
    return sorted(dict.fromkeys(absolute_links))


def write_links(output_path, links):
    with open(output_path, "w", encoding="utf-8") as file:
        for link in links:
            file.write(link + "\n")


def parse_args():
    parser = argparse.ArgumentParser(description="Download link scraper")
    parser.add_argument(
        "-o",
        "--output",
        default="download_links.txt",
        help="写入链接的输出文件，默认 download_links.txt",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    url = input("请输入要提取下载链接的网址：").strip()
    if not url:
        print("未输入网址。", file=sys.stderr)
        sys.exit(1)

    try:
        links = extract_download_links(url)
    except Exception as exc:
        print(f"抓取失败: {exc}", file=sys.stderr)
        print("请检查网络、URL 是否正确，或目标站点是否需要特殊 TLS/代理设置。", file=sys.stderr)
        sys.exit(1)

    if not links:
        print("未找到下载链接。")
        sys.exit(0)

    write_links(args.output, links)
    print(f"已写入 {len(links)} 个下载链接到 {args.output}")


if __name__ == "__main__":
    main()
