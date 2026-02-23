"""Tests for version module"""

from i18n_updater_cn.version import Version, VersionRange


class TestVersion:
    def test_parse_simple(self):
        v = Version("1.16.5")
        assert v.versions == [1, 16, 5]

    def test_parse_two_part(self):
        v = Version("1.16")
        assert v.versions == [1, 16]

    def test_parse_single(self):
        v = Version("1")
        assert v.versions == [1]

    def test_equality(self):
        assert Version("1.16.5") == Version("1.16.5")

    def test_inequality(self):
        assert Version("1.16.5") != Version("1.16.4")

    def test_less_than(self):
        assert Version("1.16.4") < Version("1.16.5")

    def test_greater_than(self):
        assert Version("1.17") > Version("1.16.5")

    def test_less_than_different_length(self):
        assert Version("1.16") < Version("1.16.5")

    def test_compare_major(self):
        assert Version("1.20") > Version("1.19.4")

    def test_equal_different_objects(self):
        a = Version("1.16.5")
        b = Version("1.16.5")
        assert a == b
        assert not a < b
        assert not a > b


class TestVersionRange:
    def test_inclusive_range(self):
        vr = VersionRange("[1.16,1.16.5]")
        assert vr.contains(Version("1.16"))
        assert vr.contains(Version("1.16.3"))
        assert vr.contains(Version("1.16.5"))

    def test_inclusive_range_outside(self):
        vr = VersionRange("[1.16,1.16.5]")
        assert not vr.contains(Version("1.15.2"))
        assert not vr.contains(Version("1.17"))

    def test_exclusive_range(self):
        vr = VersionRange("(1.16,1.16.5)")
        assert not vr.contains(Version("1.16"))
        assert vr.contains(Version("1.16.3"))
        assert not vr.contains(Version("1.16.5"))

    def test_mixed_range(self):
        vr = VersionRange("[1.16,1.16.5)")
        assert vr.contains(Version("1.16"))
        assert not vr.contains(Version("1.16.5"))

    def test_string_version_input(self):
        vr = VersionRange("[1.16,1.16.5]")
        assert vr.contains("1.16.3")

    def test_single_version_range(self):
        """Test a range that matches only a single version"""
        vr = VersionRange("[1.19.3,1.19.3]")
        assert vr.contains(Version("1.19.3"))
        assert not vr.contains(Version("1.19.2"))
        assert not vr.contains(Version("1.19.4"))

    def test_wide_range(self):
        """Test the wide range like [1.6.1,1.8.9]"""
        vr = VersionRange("[1.6.1,1.8.9]")
        assert vr.contains(Version("1.6.1"))
        assert vr.contains(Version("1.7.10"))
        assert vr.contains(Version("1.8.9"))
        assert not vr.contains(Version("1.6"))
        assert not vr.contains(Version("1.9"))

    def test_repr(self):
        vr = VersionRange("[1.16,1.16.5]")
        assert "1.16" in repr(vr)
