"""
Minecraft 汉化包更新器
根据用户指定的版本，下载或转换相应的汉化包

基于 Java 版项目 I18nUpdateMod3 重写
"""

import argparse
import logging
import os
import sys
from pathlib import Path

from .config import I18nConfig
from .resource_converter import ResourcePackConverter
from .resource_pack import ResourcePack
from .utils import FileUtil

logger = logging.getLogger(__name__)


def get_local_storage_pos() -> Path:
    """
    获取本地存储路径。
    对应 Java 版 I18nUpdateMod.getLocalStoragePos()
    """
    user_home = Path.home()

    if os.name == "nt":
        local_app_data = os.getenv("LocalAppData")
        if local_app_data:
            return Path(local_app_data)
    elif sys.platform == "darwin":
        return user_home / "Library" / "Application Support"

    # XDG_DATA_HOME, fallback to ~/.local/share
    xdg_data_home = os.getenv("XDG_DATA_HOME")
    if xdg_data_home:
        return Path(xdg_data_home)
    return user_home / ".local" / "share"


def download_or_convert_language_pack(
    minecraft_version: str,
    loader: str = "Forge",
    output_dir: str | Path | None = None,
    temp_dir: str | Path | None = None,
    debug: bool = False,
) -> dict:
    """
    下载或转换指定版本的汉化包。

    Args:
        minecraft_version: Minecraft版本号（如1.16.5）
        loader: Mod加载器类型（Forge/Fabric/Quilt）
        output_dir: 汉化包输出目录路径，如果为None则使用当前目录
        temp_dir: 临时文件目录路径，如果为None则使用系统默认位置
        debug: 是否启用调试模式

    Returns:
        dict: 包含操作结果的字典
    """
    if debug:
        logging.basicConfig(level=logging.DEBUG, format="[%(levelname)s] %(message)s")
    else:
        logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

    logger.info(
        "I18n Updater started, Minecraft version: %s, Loader: %s",
        minecraft_version,
        loader,
    )

    # 设置输出目录
    if output_dir is None:
        output_dir = Path.cwd()
    else:
        output_dir = Path(output_dir)
    FileUtil.set_resource_pack_dir(output_dir)

    # 设置临时目录
    if temp_dir is None:
        temp_dir = get_local_storage_pos() / ".i18n_updater_cn"
    else:
        temp_dir = Path(temp_dir)

    result = {
        "success": False,
        "version": minecraft_version,
        "loader": loader,
        "output_dir": str(output_dir),
        "output_file": None,
        "error": None,
    }

    try:
        # 获取该版本对应的资源包详情
        assets = I18nConfig.get_asset_detail(minecraft_version, loader)

        # 更新资源包
        language_packs: list[ResourcePack] = []
        convert_not_need = (
            len(assets.downloads) == 1
            and assets.downloads[0].target_version == minecraft_version
        )
        final_filename = assets.downloads[0].file_name

        for dl in assets.downloads:
            version_temp_dir = temp_dir / dl.target_version
            FileUtil.set_temporary_dir(version_temp_dir)

            pack = ResourcePack(dl.file_name, convert_not_need)
            pack.check_update(dl.file_url, dl.md5_url)
            language_packs.append(pack)

        # 如果需要转换资源包
        if not convert_not_need:
            FileUtil.set_temporary_dir(temp_dir / minecraft_version)
            final_filename = assets.convert_file_name
            converter = ResourcePackConverter(language_packs, final_filename)

            # 构建资源包描述
            if len(assets.downloads) > 1:
                versions_str = "和".join(
                    dl.target_version for dl in assets.downloads
                )
                description = (
                    f"该包由{versions_str}版本合并\n"
                    f"作者：CFPA团队及汉化项目贡献者"
                )
            else:
                description = (
                    f"该包对应的官方支持版本为{assets.downloads[0].target_version}\n"
                    f"作者：CFPA团队及汉化项目贡献者"
                )

            converter.convert(assets.convert_pack_format, description)

        output_file = output_dir / final_filename
        logger.info("Resource pack saved to: %s", output_file)

        result["success"] = True
        result["output_file"] = str(output_file)

    except Exception as e:
        logger.error("Failed to update resource pack: %s", e)
        result["error"] = str(e)

    return result


def cli_main() -> None:
    """命令行入口点"""
    parser = argparse.ArgumentParser(description="Minecraft 汉化包更新工具")
    parser.add_argument("version", help="Minecraft版本，例如1.16.5")
    parser.add_argument(
        "--loader",
        "-l",
        default="Forge",
        choices=["Forge", "Fabric", "Quilt"],
        help="Mod加载器类型 (默认: Forge)",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=None,
        help="汉化包输出目录路径 (默认: 当前目录)",
    )
    parser.add_argument(
        "--temp", "-t", default=None, help="临时文件目录路径 (默认: 系统默认位置)"
    )
    parser.add_argument(
        "--debug", "-d", action="store_true", help="启用调试模式"
    )

    args = parser.parse_args()

    result = download_or_convert_language_pack(
        args.version, args.loader, args.output, args.temp, args.debug
    )

    if result["success"]:
        print(f"汉化包已成功下载到:\n{result['output_file']}")
    else:
        print(f"错误: {result['error']}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    cli_main()
