"""
资源包管理模块，负责下载和校验资源包
对应 Java 版项目中的 ResourcePack.java
"""

import logging
import shutil
from pathlib import Path

from .asset_util import download, get_string, md5_hex
from .utils import FileUtil

logger = logging.getLogger(__name__)

# 限制更新检查频率（1天，单位秒）
UPDATE_TIME_GAP = 24 * 60 * 60


class ResourcePack:
    """资源包管理类"""

    def __init__(self, filename: str, save_to_game: bool = True) -> None:
        self.filename = filename
        self.save_to_game = save_to_game
        self.file_path = FileUtil.get_resource_pack_path(filename)
        self.tmp_file_path = FileUtil.get_temporary_path(filename)
        self._remote_md5: str | None = None

        try:
            FileUtil.sync_tmp_file(self.file_path, self.tmp_file_path, save_to_game)
        except Exception as e:
            logger.warning(
                "Error while sync temp file %s <-> %s: %s",
                self.file_path,
                self.tmp_file_path,
                e,
            )

    def check_update(self, file_url: str, md5_url: str) -> None:
        """检查并更新资源包"""
        if self._is_up_to_date(md5_url):
            logger.debug("Already up to date.")
            return
        self._download_full(file_url, md5_url)

    def _is_up_to_date(self, md5_url: str) -> bool:
        """
        检查资源包是否为最新版本。
        对应 Java 版 ResourcePack.isUpToDate()
        """
        import time

        if not self.tmp_file_path.exists():
            logger.debug("Local file %s not exist.", self.tmp_file_path)
            return False

        # 最近更新过，不需要再次检查
        mtime = self.tmp_file_path.stat().st_mtime
        if mtime > time.time() - UPDATE_TIME_GAP:
            logger.debug("Local file %s has been updated recently.", self.tmp_file_path)
            return True

        return self._check_md5(self.tmp_file_path, md5_url)

    def _check_md5(self, local_file: Path, md5_url: str) -> bool:
        """比较本地文件与远程 MD5"""
        local_md5 = md5_hex(local_file)
        if self._remote_md5 is None:
            self._remote_md5 = get_string(md5_url)
        logger.debug(
            "%s md5: %s, remote md5: %s", local_file, local_md5, self._remote_md5
        )
        return local_md5.lower() == self._remote_md5.lower()

    def _download_full(self, file_url: str, md5_url: str) -> None:
        """
        下载完整资源包。
        对应 Java 版 ResourcePack.downloadFull()
        """
        download_tmp = FileUtil.get_temporary_path(f"{self.filename}.tmp")
        try:
            download(file_url, download_tmp)
            if not self._check_md5(download_tmp, md5_url):
                raise IOError("Download MD5 not match")
            # 原子性移动
            shutil.move(str(download_tmp), str(self.tmp_file_path))
            logger.debug("Updates temp file: %s", self.tmp_file_path)
        except Exception as e:
            logger.warning("Error while downloading: %s", e)

        if not self.tmp_file_path.exists():
            raise FileNotFoundError(f"Tmp file not found: {self.tmp_file_path}")

        FileUtil.sync_tmp_file(self.file_path, self.tmp_file_path, self.save_to_game)

    def get_tmp_file_path(self) -> Path:
        return self.tmp_file_path

    def get_filename(self) -> str:
        return self.filename
