"""
资源包转换器，用于合并和转换资源包
对应 Java 版项目中的 ResourcePackConverter.java
"""

import json
import logging
import zipfile
from pathlib import Path

from .resource_pack import ResourcePack
from .utils import FileUtil

logger = logging.getLogger(__name__)


class ResourcePackConverter:
    """资源包转换器"""

    def __init__(
        self, resource_packs: list[ResourcePack], output_filename: str
    ) -> None:
        self.source_paths = [rp.get_tmp_file_path() for rp in resource_packs]
        self.file_path = FileUtil.get_resource_pack_path(output_filename)
        self.tmp_file_path = FileUtil.get_temporary_path(output_filename)

    def convert(self, pack_format: int, description: str) -> None:
        """
        转换资源包：合并多个源 ZIP，修改 pack.mcmeta。
        对应 Java 版 ResourcePackConverter.convert()
        """
        processed_files: set[str] = set()

        try:
            self.tmp_file_path.parent.mkdir(parents=True, exist_ok=True)

            with zipfile.ZipFile(
                self.tmp_file_path, "w", zipfile.ZIP_DEFLATED
            ) as zip_out:
                for source_path in self.source_paths:
                    logger.info("Converting: %s", source_path)

                    if not source_path.exists():
                        logger.warning("Source not found: %s", source_path)
                        continue

                    with zipfile.ZipFile(source_path, "r") as zip_in:
                        for entry in zip_in.infolist():
                            name = entry.filename

                            # 跳过重复文件
                            if name in processed_files:
                                continue
                            processed_files.add(name)

                            zip_out.putNextEntry = None  # type: ignore
                            data = zip_in.read(name)

                            if name.lower() == "pack.mcmeta":
                                # 修改 pack.mcmeta
                                data = self._convert_pack_meta(
                                    data, pack_format, description
                                )

                            zip_out.writestr(name, data)

            logger.info(
                "Converted: %s -> %s", self.source_paths, self.tmp_file_path
            )
            FileUtil.sync_tmp_file(self.tmp_file_path, self.file_path, True)

        except Exception as e:
            raise Exception(
                f"Error converting {self.source_paths} to {self.tmp_file_path}: {e}"
            ) from e

    @staticmethod
    def _convert_pack_meta(
        data: bytes, pack_format: int, description: str
    ) -> bytes:
        """修改 pack.mcmeta 的 pack_format 和 description"""
        meta = json.loads(data.decode("utf-8"))
        meta["pack"]["pack_format"] = pack_format
        meta["pack"]["description"] = description
        return json.dumps(meta, indent=2, ensure_ascii=False).encode("utf-8")
