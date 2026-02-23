"""Tests for FileUtil"""

import tempfile
import time
from pathlib import Path

from i18n_updater_cn.utils import FileUtil


class TestFileUtil:
    def test_set_and_get_resource_pack_dir(self, tmp_path):
        FileUtil.set_resource_pack_dir(tmp_path)
        result = FileUtil.get_resource_pack_path("test.zip")
        assert result == tmp_path / "test.zip"

    def test_set_and_get_temporary_dir(self, tmp_path):
        FileUtil.set_temporary_dir(tmp_path)
        result = FileUtil.get_temporary_path("test.zip")
        assert result == tmp_path / "test.zip"

    def test_get_resource_pack_path_raises_if_not_set(self):
        FileUtil._resource_pack_dir = None
        try:
            FileUtil.get_resource_pack_path("test.zip")
            assert False, "Should have raised ValueError"
        except ValueError:
            pass

    def test_get_temporary_path_raises_if_not_set(self):
        FileUtil._temporary_dir = None
        try:
            FileUtil.get_temporary_path("test.zip")
            assert False, "Should have raised ValueError"
        except ValueError:
            pass

    def test_sync_tmp_file_both_not_exist(self, tmp_path):
        """When both files don't exist, nothing should happen"""
        file_a = tmp_path / "a.zip"
        file_b = tmp_path / "b.zip"
        # Should not raise
        FileUtil.sync_tmp_file(file_a, file_b, True)

    def test_sync_tmp_file_only_tmp_exists(self, tmp_path):
        """When only tmp exists, should copy to file_path"""
        file_path = tmp_path / "output" / "pack.zip"
        tmp_path_file = tmp_path / "tmp" / "pack.zip"
        tmp_path_file.parent.mkdir(parents=True)
        tmp_path_file.write_bytes(b"test content")

        FileUtil.sync_tmp_file(file_path, tmp_path_file, True)
        assert file_path.exists()
        assert file_path.read_bytes() == b"test content"

    def test_sync_tmp_file_only_file_exists(self, tmp_path):
        """When only file_path exists, should copy to tmp"""
        file_path = tmp_path / "output" / "pack.zip"
        file_path.parent.mkdir(parents=True)
        file_path.write_bytes(b"existing content")

        tmp_path_file = tmp_path / "tmp" / "pack.zip"

        FileUtil.sync_tmp_file(file_path, tmp_path_file, True)
        assert tmp_path_file.exists()
        assert tmp_path_file.read_bytes() == b"existing content"

    def test_sync_tmp_file_no_save_to_game(self, tmp_path):
        """When save_to_game is False and target is file_path, should skip"""
        file_path = tmp_path / "output" / "pack.zip"
        tmp_path_file = tmp_path / "tmp" / "pack.zip"
        tmp_path_file.parent.mkdir(parents=True)
        tmp_path_file.write_bytes(b"tmp content")

        FileUtil.sync_tmp_file(file_path, tmp_path_file, False)
        # file_path should NOT be created when save_to_game is False
        assert not file_path.exists()

    def test_creates_directory_on_set(self, tmp_path):
        new_dir = tmp_path / "new" / "nested" / "dir"
        FileUtil.set_resource_pack_dir(new_dir)
        assert new_dir.exists()
