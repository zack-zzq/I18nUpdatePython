"""
网络资源工具模块
对应 Java 版项目中的 AssetUtil.java
"""

import hashlib
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import httpx

logger = logging.getLogger(__name__)

CFPA_ASSET_ROOT = "http://downloader1.meitangdehulu.com:22943/"

MIRRORS = [
    "https://raw.githubusercontent.com/",
    # 此镜像源维护者：502y
    "http://8.137.167.65:64684/",
]

GIT_INDEX_URL = (
    "https://raw.githubusercontent.com/"
    "CFPAOrg/Minecraft-Mod-Language-Package/refs/heads/index/version-index.json"
)


def _test_url_connection(url: str) -> str | None:
    """测试 URL 连通性，返回可达的 URL 或 None"""
    try:
        resp = httpx.head(url, timeout=3.0, follow_redirects=True)
        if 200 <= resp.status_code < 300:
            return url
        logger.debug("URL unreachable: %s, code: %d", url, resp.status_code)
    except Exception:
        logger.debug("URL unreachable: %s", url)
    return None


def get_fastest_url() -> str:
    """
    并行测试所有镜像源，返回最快可达的 URL。
    对应 Java 版 AssetUtil.getFastestUrl()
    """
    urls = list(MIRRORS) + [CFPA_ASSET_ROOT]

    with ThreadPoolExecutor(max_workers=max(len(urls), 10)) as executor:
        futures = {executor.submit(_test_url_connection, url): url for url in urls}

        for future in as_completed(futures):
            result = future.result()
            if result is not None:
                logger.info("Using fastest url: %s", result)
                # 取消剩余任务
                for f in futures:
                    f.cancel()
                return result

    # 全部失败，返回默认 URL
    logger.info("All urls are unreachable, using CFPA_ASSET_ROOT")
    return CFPA_ASSET_ROOT


def download(url: str, local_file: Path) -> None:
    """下载文件到本地路径"""
    logger.info("Downloading: %s -> %s", url, local_file)
    local_file.parent.mkdir(parents=True, exist_ok=True)
    with httpx.stream("GET", url, timeout=33.0, follow_redirects=True) as resp:
        resp.raise_for_status()
        with open(local_file, "wb") as f:
            for chunk in resp.iter_bytes(chunk_size=8192):
                f.write(chunk)
    logger.debug("Downloaded: %s -> %s", url, local_file)


def get_string(url: str) -> str:
    """获取远程 URL 的文本内容"""
    resp = httpx.get(url, timeout=10.0, follow_redirects=True)
    resp.raise_for_status()
    return resp.text.strip()


def get_git_index() -> dict[str, str]:
    """
    获取 GitHub Release 版本索引。
    对应 Java 版 AssetUtil.getGitIndex()
    """
    try:
        resp = httpx.get(GIT_INDEX_URL, timeout=5.0, follow_redirects=True)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return {}


def md5_hex(file_path: Path) -> str:
    """计算文件的 MD5 哈希值"""
    md5_hash = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4 * 1024 * 1024), b""):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()
