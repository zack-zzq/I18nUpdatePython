"""Tests for config module"""

from i18n_updater_cn.config import I18nConfig, GameAssetDetail, AssetDownloadDetail


class TestI18nConfig:
    def test_load_metadata(self):
        """Metadata should load from embedded JSON"""
        metadata = I18nConfig._load_metadata()
        assert "games" in metadata
        assert "assets" in metadata
        assert len(metadata["games"]) > 0
        assert len(metadata["assets"]) > 0

    def test_get_game_metadata_1_12_2(self):
        meta = I18nConfig._get_game_metadata("1.12.2")
        assert meta["packFormat"] == 3
        assert "1.12.2" in meta["convertFrom"]

    def test_get_game_metadata_1_20_1(self):
        meta = I18nConfig._get_game_metadata("1.20.1")
        assert meta["packFormat"] == 15
        assert "1.20" in meta["convertFrom"]

    def test_get_game_metadata_1_6_4(self):
        meta = I18nConfig._get_game_metadata("1.6.4")
        assert meta["packFormat"] == 1

    def test_get_game_metadata_invalid_version(self):
        try:
            I18nConfig._get_game_metadata("99.99.99")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "99.99.99" in str(e)

    def test_get_asset_metadata_forge(self):
        asset = I18nConfig._get_asset_metadata("1.20", "Forge")
        assert asset["loader"] == "Forge"
        assert "1-20" in asset["filename"]

    def test_get_asset_metadata_fabric(self):
        asset = I18nConfig._get_asset_metadata("1.20", "Fabric")
        assert asset["loader"] == "Fabric"
        assert "Fabric" in asset["filename"]

    def test_get_asset_metadata_fallback(self):
        """Should fallback to first asset if loader doesn't match"""
        asset = I18nConfig._get_asset_metadata("1.12.2", "Fabric")
        # 1.12.2 only has Forge, should fall back
        assert asset is not None
        assert asset["targetVersion"] == "1.12.2"

    def test_get_asset_detail_returns_dataclass(self):
        """Test that get_asset_detail returns a GameAssetDetail"""
        # Force CFPA_ASSET_ROOT to avoid network calls in test
        import i18n_updater_cn.config as config_mod
        original = config_mod.get_fastest_url

        try:
            config_mod.get_fastest_url = lambda: "http://downloader1.meitangdehulu.com:22943/"
            detail = I18nConfig.get_asset_detail("1.12.2", "Forge")
            assert isinstance(detail, GameAssetDetail)
            assert len(detail.downloads) > 0
            assert isinstance(detail.downloads[0], AssetDownloadDetail)
            assert detail.convert_pack_format == 3
        finally:
            config_mod.get_fastest_url = original

    def test_get_asset_detail_single_version(self):
        """1.12.2 converts from only 1.12.2, so it should be a single download"""
        import i18n_updater_cn.config as config_mod
        original = config_mod.get_fastest_url

        try:
            config_mod.get_fastest_url = lambda: "http://downloader1.meitangdehulu.com:22943/"
            detail = I18nConfig.get_asset_detail("1.12.2", "Forge")
            assert len(detail.downloads) == 1
            assert detail.downloads[0].target_version == "1.12.2"
        finally:
            config_mod.get_fastest_url = original

    def test_get_asset_detail_multi_version(self):
        """1.20.1 converts from 1.20 + 1.19 + 1.18, so 3 downloads"""
        import i18n_updater_cn.config as config_mod
        original = config_mod.get_fastest_url

        try:
            config_mod.get_fastest_url = lambda: "http://downloader1.meitangdehulu.com:22943/"
            detail = I18nConfig.get_asset_detail("1.20.1", "Forge")
            assert len(detail.downloads) == 3
            versions = [d.target_version for d in detail.downloads]
            assert "1.20" in versions
            assert "1.19" in versions
            assert "1.18" in versions
        finally:
            config_mod.get_fastest_url = original
