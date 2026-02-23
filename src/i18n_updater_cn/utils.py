"""
文件操作工具模块
对应 Java 版项目中的 FileUtil.java
"""

import logging
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)


class FileUtil:
    """文件操作工具，管理资源包目录和临时目录"""

    _resource_pack_dir: Path | None = None
    _temporary_dir: Path | None = None

    @classmethod
    def set_resource_pack_dir(cls, path: Path) -> None:
        """设置资源包目录"""
        abs_path = Path(path).resolve()
        cls._safe_create_dir(abs_path)
        cls._resource_pack_dir = abs_path

    @classmethod
    def set_temporary_dir(cls, path: Path) -> None:
        """设置临时目录"""
        abs_path = Path(path).resolve()
        cls._safe_create_dir(abs_path)
        cls._temporary_dir = abs_path

    @staticmethod
    def _safe_create_dir(path: Path) -> None:
        """安全地创建目录"""
        try:
            path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.warning("Cannot create dir: %s", e)

    @classmethod
    def get_resource_pack_path(cls, filename: str) -> Path:
        """获取资源包路径"""
        if cls._resource_pack_dir is None:
            raise ValueError("Resource pack directory not set")
        return cls._resource_pack_dir / filename

    @classmethod
    def get_temporary_path(cls, filename: str) -> Path:
        """获取临时文件路径"""
        if cls._temporary_dir is None:
            raise ValueError("Temporary directory not set")
        return cls._temporary_dir / filename

    @classmethod
    def sync_tmp_file(
        cls, file_path: Path, tmp_file_path: Path, save_to_game: bool = True
    ) -> None:
        """
        同步临时文件和目标文件。
        对应 Java 版 FileUtil.syncTmpFile()
        """
        file_path = Path(file_path)
        tmp_file_path = Path(tmp_file_path)

        # 两个文件都不存在
        if not file_path.exists() and not tmp_file_path.exists():
            logger.debug("Both temp and current file not found")
            return

        # 比较确定哪个更新
        if file_path.exists() and tmp_file_path.exists():
            file_mtime = file_path.stat().st_mtime
            tmp_mtime = tmp_file_path.stat().st_mtime

            if abs(file_mtime - tmp_mtime) < 1:
                logger.debug("Temp and current file has already been synchronized")
                return

            if file_mtime > tmp_mtime:
                source, target = file_path, tmp_file_path
            else:
                source, target = tmp_file_path, file_path
        elif file_path.exists():
            source, target = file_path, tmp_file_path
        else:
            source, target = tmp_file_path, file_path

        # 如果不需要保存到游戏且目标是游戏文件，则跳过
        if not save_to_game and target == file_path:
            return

        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        logger.info("Synchronized: %s -> %s", source, target)
