"""
配置管理模块，负责解析元数据和处理版本匹配
对应 Java 版项目中的 I18nConfig.java
"""

from __future__ import annotations

import json
import logging
from importlib import resources
from dataclasses import dataclass, field

from .asset_util import CFPA_ASSET_ROOT, get_fastest_url, get_git_index
from .version import Version, VersionRange

logger = logging.getLogger(__name__)


@dataclass
class AssetDownloadDetail:
    file_name: str
    file_url: str
    md5_url: str
    target_version: str


@dataclass
class GameAssetDetail:
    downloads: list[AssetDownloadDetail] = field(default_factory=list)
    convert_pack_format: int = 0
    convert_file_name: str = ""


class I18nConfig:
    """配置管理类"""

    _i18n_metadata: dict | None = None

    @classmethod
    def _load_metadata(cls) -> dict:
        """从内嵌的 i18nMetaData.json 加载元数据"""
        if cls._i18n_metadata is not None:
            return cls._i18n_metadata

        ref = resources.files("i18n_updater_cn").joinpath("i18nMetaData.json")
        cls._i18n_metadata = json.loads(ref.read_text(encoding="utf-8"))
        return cls._i18n_metadata

    @classmethod
    def _get_game_metadata(cls, minecraft_version: str) -> dict:
        """获取指定 Minecraft 版本的游戏元数据"""
        metadata = cls._load_metadata()
        version = Version(minecraft_version)

        for game_meta in metadata["games"]:
            version_range = VersionRange(game_meta["gameVersions"])
            if version_range.contains(version):
                return game_meta

        raise ValueError(
            f"Version {minecraft_version} not found in i18n meta"
        )

    @classmethod
    def _get_asset_metadata(cls, target_version: str, loader: str) -> dict:
        """获取特定版本和加载器的资源包元数据"""
        metadata = cls._load_metadata()

        matching = [
            a
            for a in metadata["assets"]
            if a["targetVersion"] == target_version
        ]

        if not matching:
            raise ValueError(
                f"No asset found for version {target_version}"
            )

        # 优先匹配 loader，否则返回第一个
        for asset in matching:
            if asset["loader"].lower() == loader.lower():
                return asset
        return matching[0]

    @classmethod
    def get_asset_detail(
        cls, minecraft_version: str, loader: str
    ) -> GameAssetDetail:
        """
        根据 Minecraft 版本和加载器类型获取资源包详情。
        对应 Java 版 I18nConfig.getAssetDetail()
        """
        game_meta = cls._get_game_metadata(minecraft_version)

        asset_root = get_fastest_url()
        logger.debug("Using asset root: %s", asset_root)

        if asset_root == "https://raw.githubusercontent.com/":
            downloads = cls._create_download_details_from_git(
                game_meta, loader
            )
        else:
            downloads = cls._create_download_details(
                game_meta, loader, asset_root
            )

        return GameAssetDetail(
            downloads=downloads,
            convert_pack_format=game_meta["packFormat"],
            convert_file_name=f"Minecraft-Mod-Language-Modpack-Converted-{minecraft_version}.zip",
        )

    @classmethod
    def _create_download_details(
        cls, game_meta: dict, loader: str, asset_root: str
    ) -> list[AssetDownloadDetail]:
        """创建下载详情列表"""
        details = []
        for version in game_meta["convertFrom"]:
            asset = cls._get_asset_metadata(version, loader)
            details.append(
                AssetDownloadDetail(
                    file_name=asset["filename"],
                    file_url=asset_root + asset["filename"],
                    md5_url=asset_root + asset["md5Filename"],
                    target_version=asset["targetVersion"],
                )
            )
        return details

    @classmethod
    def _create_download_details_from_git(
        cls, game_meta: dict, loader: str
    ) -> list[AssetDownloadDetail]:
        """
        从 GitHub Release 创建下载详情列表。
        对应 Java 版 I18nConfig.createDownloadDetailsFromGit()
        """
        try:
            index = get_git_index()
            version = game_meta["convertFrom"][0]

            if "fabric" in loader.lower():
                release_tag = index.get(f"{version}-fabric")
            else:
                release_tag = index.get(version)

            if release_tag is None:
                logger.debug("Error getting index: %s-%s", version, loader)
                raise KeyError(f"No release tag for {version}-{loader}")

            asset_root = (
                f"https://github.com/CFPAOrg/Minecraft-Mod-Language-Package/"
                f"releases/download/{release_tag}/"
            )

            return cls._create_download_details(game_meta, loader, asset_root)

        except Exception:
            # 回退到 CFPA 默认源
            return cls._create_download_details(
                game_meta, loader, CFPA_ASSET_ROOT
            )
