# SPDX-FileCopyrightText: 2021 The pypa/build developers
# SPDX-FileCopyrightText: 2023 Filipe Laíns <lains@riseup.net>
#
# SPDX-License-Identifier: MIT

import sys
import textwrap

import pytest

import ffy00.packaging


if sys.version_info >= (3, 8):
    import importlib.metadata as importlib_metadata
else:
    import importlib_metadata


class MockDistribution(importlib_metadata.Distribution):
    def locate_file(self, path):  # pragma: no cover
        return ''

    @classmethod
    def from_name(cls, name):
        if name == 'extras_dep':
            return ExtraMockDistribution()
        elif name == 'requireless_dep':
            return RequirelessMockDistribution()
        elif name == 'recursive_dep':
            return RecursiveMockDistribution()
        elif name == 'prerelease_dep':
            return PrereleaseMockDistribution()
        elif name == 'circular_dep':
            return CircularMockDistribution()
        elif name == 'nested_circular_dep':
            return NestedCircularMockDistribution()
        raise importlib_metadata.PackageNotFoundError


class ExtraMockDistribution(MockDistribution):
    def read_text(self, filename):
        if filename == 'METADATA':
            return textwrap.dedent(
                """
                Metadata-Version: 2.2
                Name: extras_dep
                Version: 1.0.0
                Provides-Extra: extra-without-associated-deps
                Provides-Extra: extra-with_unmet-deps
                Requires-Dist: unmet_dep; extra == 'extra-with-unmet-deps'
                Provides-Extra: extra-with-met-deps
                Requires-Dist: extras_dep; extra == 'extra-with-met-deps'
                Provides-Extra: recursive-extra-with-unmet-deps
                Requires-Dist: recursive_dep; extra == 'recursive-extra-with-unmet-deps'
                """
            ).strip()


class RequirelessMockDistribution(MockDistribution):
    def read_text(self, filename):
        if filename == 'METADATA':
            return textwrap.dedent(
                """
                Metadata-Version: 2.2
                Name: requireless_dep
                Version: 1.0.0
                """
            ).strip()


class RecursiveMockDistribution(MockDistribution):
    def read_text(self, filename):
        if filename == 'METADATA':
            return textwrap.dedent(
                """
                Metadata-Version: 2.2
                Name: recursive_dep
                Version: 1.0.0
                Requires-Dist: recursive_unmet_dep
                """
            ).strip()


class PrereleaseMockDistribution(MockDistribution):
    def read_text(self, filename):
        if filename == 'METADATA':
            return textwrap.dedent(
                """
                Metadata-Version: 2.2
                Name: prerelease_dep
                Version: 1.0.1a0
                """
            ).strip()


class CircularMockDistribution(MockDistribution):
    def read_text(self, filename):
        if filename == 'METADATA':
            return textwrap.dedent(
                """
                Metadata-Version: 2.2
                Name: circular_dep
                Version: 1.0.0
                Requires-Dist: nested_circular_dep
                """
            ).strip()


class NestedCircularMockDistribution(MockDistribution):
    def read_text(self, filename):
        if filename == 'METADATA':
            return textwrap.dedent(
                """
                Metadata-Version: 2.2
                Name: nested_circular_dep
                Version: 1.0.0
                Requires-Dist: circular_dep
                """
            ).strip()


@pytest.mark.parametrize(
    ('requirement_string', 'expected'),
    [
        ('extras_dep', None),
        ('missing_dep', ('missing_dep',)),
        ('requireless_dep', None),
        ('extras_dep[undefined_extra]', None),
        ('extras_dep[extra-without-associated-deps]', None),
        (
            'extras_dep[extra-with-unmet-deps]',
            ('extras_dep[extra-with-unmet-deps]', 'unmet_dep; extra == "extra-with-unmet-deps"'),
        ),
        (
            'extras_dep[recursive-extra-with-unmet-deps]',
            (
                'extras_dep[recursive-extra-with-unmet-deps]',
                'recursive_dep; extra == "recursive-extra-with-unmet-deps"',
                'recursive_unmet_dep',
            ),
        ),
        ('extras_dep[extra-with-met-deps]', None),
        ('missing_dep; python_version>"10"', None),
        ('missing_dep; python_version<="1"', None),
        ('missing_dep; python_version>="1"', ('missing_dep; python_version >= "1"',)),
        ('extras_dep == 1.0.0', None),
        ('extras_dep == 2.0.0', ('extras_dep==2.0.0',)),
        ('extras_dep[extra-without-associated-deps] == 1.0.0', None),
        ('extras_dep[extra-without-associated-deps] == 2.0.0', ('extras_dep[extra-without-associated-deps]==2.0.0',)),
        ('prerelease_dep >= 1.0.0', None),
        ('circular_dep', None),
    ],
)
def test_check_dependency(monkeypatch, requirement_string, expected):
    monkeypatch.setattr(importlib_metadata, 'Distribution', MockDistribution)
    assert next(ffy00.packaging.check_dependency(requirement_string), None) == expected
