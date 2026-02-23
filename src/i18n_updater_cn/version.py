"""
版本号解析和比较
对应 Java 版项目中的 Version.java 和 VersionRange.java
"""

from __future__ import annotations

import re


class Version:
    """版本号类，用于解析和比较版本号"""

    def __init__(self, version_str: str) -> None:
        self.version_str = version_str
        self.versions: list[int] = []
        self._parse_version(version_str)

    def _parse_version(self, version_str: str) -> None:
        """解析版本字符串，例如 '1.16.5' -> [1, 16, 5]"""
        self.versions = [int(n) for n in re.findall(r"\d+", version_str)]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        return self.versions == other.versions

    def __lt__(self, other: Version) -> bool:
        min_len = min(len(self.versions), len(other.versions))
        for i in range(min_len):
            if self.versions[i] != other.versions[i]:
                return self.versions[i] < other.versions[i]
        return len(self.versions) < len(other.versions)

    def __le__(self, other: Version) -> bool:
        return self < other or self == other

    def __gt__(self, other: Version) -> bool:
        return not self <= other

    def __ge__(self, other: Version) -> bool:
        return not self < other

    def __str__(self) -> str:
        return self.version_str

    def __repr__(self) -> str:
        return f"Version({self.version_str})"


class VersionRange:
    """版本范围类，用于判断版本是否在指定范围内"""

    def __init__(self, range_str: str) -> None:
        self.range_str = range_str
        self.from_version: Version | None = None
        self.to_version: Version | None = None
        self.contains_left = False
        self.contains_right = False
        self._parse_version_range(range_str)

    def _parse_version_range(self, range_str: str) -> None:
        """
        解析版本范围字符串

        格式：
        - "[1.16,1.16.5]" 表示 1.16 <= version <= 1.16.5
        - "(1.16,1.16.5)" 表示 1.16 < version < 1.16.5
        """
        if range_str.startswith("["):
            self.contains_left = True
        elif range_str.startswith("("):
            self.contains_left = False
        else:
            raise ValueError(f"Invalid version range: {range_str}")

        if range_str.endswith("]"):
            self.contains_right = True
        elif range_str.endswith(")"):
            self.contains_right = False
        else:
            raise ValueError(f"Invalid version range: {range_str}")

        versions_part = range_str[1:-1]
        if "," not in versions_part:
            raise ValueError(f"Invalid version range (missing comma): {range_str}")

        from_str, to_str = versions_part.split(",", 1)

        if from_str:
            self.from_version = Version(from_str)
        if to_str:
            self.to_version = Version(to_str)

    def contains(self, version: Version | str) -> bool:
        """判断给定版本是否在范围内"""
        if isinstance(version, str):
            version = Version(version)

        if self.from_version is not None:
            cmp = version.__eq__(self.from_version)
            if version < self.from_version:
                return False
            if not self.contains_left and version == self.from_version:
                return False

        if self.to_version is not None:
            if version > self.to_version:
                return False
            if not self.contains_right and version == self.to_version:
                return False

        return True

    def __str__(self) -> str:
        return self.range_str

    def __repr__(self) -> str:
        return f"VersionRange({self.range_str})"
