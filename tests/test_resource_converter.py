"""Tests for ResourcePackConverter"""

import json
import zipfile
from pathlib import Path
from unittest.mock import MagicMock

from i18n_updater_cn.resource_converter import ResourcePackConverter
from i18n_updater_cn.utils import FileUtil


def _create_test_zip(path: Path, files: dict, pack_format: int = 1) -> None:
    """Helper to create a test ZIP with given files and pack.mcmeta"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w") as zf:
        # Add pack.mcmeta
        meta = {"pack": {"pack_format": pack_format, "description": "Test pack"}}
        zf.writestr("pack.mcmeta", json.dumps(meta))
        # Add other files
        for name, content in files.items():
            zf.writestr(name, content)


class TestResourcePackConverter:
    def setup_method(self):
        FileUtil._resource_pack_dir = None
        FileUtil._temporary_dir = None

    def test_convert_single_source(self, tmp_path):
        """Converting a single source should rewrite pack.mcmeta"""
        FileUtil.set_resource_pack_dir(tmp_path / "output")
        FileUtil.set_temporary_dir(tmp_path / "tmp")

        # Create source ZIP
        source = tmp_path / "source" / "source.zip"
        _create_test_zip(source, {"assets/lang/en_us.json": '{"key": "value"}'})

        # Create mock ResourcePack
        mock_pack = MagicMock()
        mock_pack.get_tmp_file_path.return_value = source

        converter = ResourcePackConverter([mock_pack], "output.zip")
        converter.convert(15, "Test description")

        # Verify output exists
        output = tmp_path / "tmp" / "output.zip"
        assert output.exists()

        # Verify pack.mcmeta was updated
        with zipfile.ZipFile(output) as zf:
            meta = json.loads(zf.read("pack.mcmeta"))
            assert meta["pack"]["pack_format"] == 15
            assert meta["pack"]["description"] == "Test description"

            # Verify other files preserved
            assert "assets/lang/en_us.json" in zf.namelist()

    def test_convert_multiple_sources_dedup(self, tmp_path):
        """Converting multiple sources should deduplicate files"""
        FileUtil.set_resource_pack_dir(tmp_path / "output")
        FileUtil.set_temporary_dir(tmp_path / "tmp")

        # Create two source ZIPs with overlapping files
        source1 = tmp_path / "source" / "s1.zip"
        _create_test_zip(
            source1,
            {
                "assets/lang/en_us.json": '{"key": "primary"}',
                "assets/lang/zh_cn.json": '{"key": "primary_cn"}',
            },
        )

        source2 = tmp_path / "source" / "s2.zip"
        _create_test_zip(
            source2,
            {
                "assets/lang/en_us.json": '{"key": "secondary"}',
                "assets/lang/de_de.json": '{"key": "german"}',
            },
        )

        mock1 = MagicMock()
        mock1.get_tmp_file_path.return_value = source1
        mock2 = MagicMock()
        mock2.get_tmp_file_path.return_value = source2

        converter = ResourcePackConverter([mock1, mock2], "merged.zip")
        converter.convert(15, "Merged")

        output = tmp_path / "tmp" / "merged.zip"
        with zipfile.ZipFile(output) as zf:
            # en_us.json should contain primary (from first ZIP)
            content = zf.read("assets/lang/en_us.json").decode()
            assert "primary" in content
            assert "secondary" not in content

            # de_de.json should exist (from second ZIP)
            assert "assets/lang/de_de.json" in zf.namelist()

            # zh_cn.json should exist (from first ZIP)
            assert "assets/lang/zh_cn.json" in zf.namelist()

    def test_convert_missing_source_skipped(self, tmp_path):
        """Missing source files should be skipped without error"""
        FileUtil.set_resource_pack_dir(tmp_path / "output")
        FileUtil.set_temporary_dir(tmp_path / "tmp")

        # Create one real source and one nonexistent
        real_source = tmp_path / "source" / "real.zip"
        _create_test_zip(real_source, {"assets/test.txt": "content"})

        mock_real = MagicMock()
        mock_real.get_tmp_file_path.return_value = real_source
        mock_missing = MagicMock()
        mock_missing.get_tmp_file_path.return_value = tmp_path / "nonexistent.zip"

        converter = ResourcePackConverter([mock_real, mock_missing], "out.zip")
        converter.convert(15, "Test")

        output = tmp_path / "tmp" / "out.zip"
        assert output.exists()
