# SPDX-FileCopyrightText: 2021 The pypa/build developers
# SPDX-FileCopyrightText: 2023 Filipe Laíns <lains@riseup.net>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import sys

from collections.abc import Iterator, Set

import packaging.requirements


if sys.version_info >= (3, 8):
    import importlib.metadata as importlib_metadata
else:
    import importlib_metadata


__version__ = '0.1.0'


# Originally taken from the pypa/build project
# https://github.com/pypa/build/blob/e496fe6342f0e4729b69d0ea93eef529f27875a6/src/build/_util.py#L16
def check_dependency(
    req_string: str,
    ancestral_req_strings: tuple[str, ...] = (),
    parent_extras: Set[str] = frozenset(),
) -> Iterator[tuple[str, ...]]:
    """
    Verify that a dependency and all of its dependencies are met.

    :param req_string: Requirement string
    :param parent_extras: Extras (eg. "test" in ``myproject[test]``)
    :yields: Unmet dependencies
    """
    req = packaging.requirements.Requirement(req_string)
    normalised_req_string = str(req)

    # ``Requirement`` doesn't implement ``__eq__`` so we cannot compare reqs for
    # equality directly but the string representation is stable.
    if normalised_req_string in ancestral_req_strings:
        # cyclical dependency, already checked.
        return

    if req.marker:
        extras = frozenset(('',)).union(parent_extras)
        # a requirement can have multiple extras but ``evaluate`` can
        # only check one at a time.
        if all(not req.marker.evaluate(environment={'extra': e}) for e in extras):
            # if the marker conditions are not met, we pretend that the
            # dependency is satisfied.
            return

    try:
        dist = importlib_metadata.distribution(req.name)  # type: ignore[no-untyped-call]
    except importlib_metadata.PackageNotFoundError:
        # dependency is not installed in the environment.
        yield (*ancestral_req_strings, normalised_req_string)
    else:
        if req.specifier and not req.specifier.contains(dist.version, prereleases=True):
            # the installed version is incompatible.
            yield (*ancestral_req_strings, normalised_req_string)
        elif dist.requires:
            for other_req_string in dist.requires:
                # yields transitive dependencies that are not satisfied.
                yield from check_dependency(other_req_string, (*ancestral_req_strings, normalised_req_string), req.extras)
