"""Tests for asset_util module"""

import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from i18n_updater_cn.asset_util import (
    get_fastest_url,
    md5_hex,
    CFPA_ASSET_ROOT,
    _test_url_connection,
)


class TestMd5Hex:
    def test_md5_known_content(self):
        """Test MD5 of a file with known content"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as f:
            f.write(b"hello world")
            f.flush()
            path = Path(f.name)

        md5 = md5_hex(path)
        # MD5 of "hello world" is 5eb63bbbe01eeed093cb22bb8f5acdc3
        assert md5 == "5eb63bbbe01eeed093cb22bb8f5acdc3"
        path.unlink()

    def test_md5_empty_file(self):
        """Test MD5 of an empty file"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as f:
            path = Path(f.name)

        md5 = md5_hex(path)
        # MD5 of empty string is d41d8cd98f00b204e9800998ecf8427e
        assert md5 == "d41d8cd98f00b204e9800998ecf8427e"
        path.unlink()


class TestGetFastestUrl:
    @patch("i18n_updater_cn.asset_util._test_url_connection")
    def test_returns_first_successful(self, mock_test):
        """Should return the first URL that succeeds"""
        # Make all URLs return None except the last one
        def side_effect(url):
            if "downloader1" in url:
                return url
            return None

        mock_test.side_effect = side_effect
        result = get_fastest_url()
        assert result == CFPA_ASSET_ROOT

    @patch("i18n_updater_cn.asset_util._test_url_connection")
    def test_returns_default_when_all_fail(self, mock_test):
        """Should return CFPA_ASSET_ROOT when all mirrors fail"""
        mock_test.return_value = None
        result = get_fastest_url()
        assert result == CFPA_ASSET_ROOT


class TestTestUrlConnection:
    @patch("i18n_updater_cn.asset_util.httpx.head")
    def test_success(self, mock_head):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_head.return_value = mock_response

        result = _test_url_connection("http://example.com")
        assert result == "http://example.com"

    @patch("i18n_updater_cn.asset_util.httpx.head")
    def test_failure_status(self, mock_head):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_head.return_value = mock_response

        result = _test_url_connection("http://example.com")
        assert result is None

    @patch("i18n_updater_cn.asset_util.httpx.head")
    def test_failure_exception(self, mock_head):
        mock_head.side_effect = Exception("Connection error")
        result = _test_url_connection("http://example.com")
        assert result is None
