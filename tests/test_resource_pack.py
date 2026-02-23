"""Tests for ResourcePack"""

import time
from pathlib import Path
from unittest.mock import patch

from i18n_updater_cn.resource_pack import ResourcePack, UPDATE_TIME_GAP
from i18n_updater_cn.utils import FileUtil


class TestResourcePack:
    def setup_method(self):
        """Reset FileUtil state before each test"""
        FileUtil._resource_pack_dir = None
        FileUtil._temporary_dir = None

    def test_is_up_to_date_file_not_exist(self, tmp_path):
        """Should return False when tmp file doesn't exist"""
        FileUtil.set_resource_pack_dir(tmp_path / "output")
        FileUtil.set_temporary_dir(tmp_path / "tmp")

        pack = ResourcePack("test.zip", save_to_game=False)
        assert not pack._is_up_to_date("http://example.com/test.md5")

    @patch("i18n_updater_cn.resource_pack.get_string")
    @patch("i18n_updater_cn.resource_pack.md5_hex")
    def test_is_up_to_date_recently_modified(self, mock_md5, mock_get_string, tmp_path):
        """Should return True when file was recently modified"""
        FileUtil.set_resource_pack_dir(tmp_path / "output")
        FileUtil.set_temporary_dir(tmp_path / "tmp")

        # Create the tmp file
        tmp_file = tmp_path / "tmp" / "test.zip"
        tmp_file.write_bytes(b"content")

        pack = ResourcePack("test.zip", save_to_game=False)
        result = pack._is_up_to_date("http://example.com/test.md5")
        assert result is True
        # Should not have called MD5 functions
        mock_md5.assert_not_called()
        mock_get_string.assert_not_called()

    @patch("i18n_updater_cn.resource_pack.get_string")
    @patch("i18n_updater_cn.resource_pack.md5_hex")
    def test_check_md5_match(self, mock_md5, mock_get_string, tmp_path):
        """Should return True when MD5s match"""
        FileUtil.set_resource_pack_dir(tmp_path / "output")
        FileUtil.set_temporary_dir(tmp_path / "tmp")

        tmp_file = tmp_path / "tmp" / "test.zip"
        tmp_file.write_bytes(b"content")

        mock_md5.return_value = "abc123def456"
        mock_get_string.return_value = "ABC123DEF456"

        pack = ResourcePack("test.zip", save_to_game=False)
        result = pack._check_md5(tmp_file, "http://example.com/test.md5")
        assert result is True

    @patch("i18n_updater_cn.resource_pack.get_string")
    @patch("i18n_updater_cn.resource_pack.md5_hex")
    def test_check_md5_mismatch(self, mock_md5, mock_get_string, tmp_path):
        """Should return False when MD5s don't match"""
        FileUtil.set_resource_pack_dir(tmp_path / "output")
        FileUtil.set_temporary_dir(tmp_path / "tmp")

        tmp_file = tmp_path / "tmp" / "test.zip"
        tmp_file.write_bytes(b"content")

        mock_md5.return_value = "abc123"
        mock_get_string.return_value = "xyz789"

        pack = ResourcePack("test.zip", save_to_game=False)
        result = pack._check_md5(tmp_file, "http://example.com/test.md5")
        assert result is False
