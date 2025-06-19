#!/usr/bin/python3

# Copyright (C) 2021 Canonical Ltd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3, as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import logging
import lxml.html
import sys
from http import HTTPStatus
from packaging import version
from urllib import request


ROOT_URL = "https://ftp.mozilla.org/pub/firefox/candidates/"

BETA = "beta"
RELEASE = "release"
ESR = "esr"
CHANNELS = (BETA, RELEASE, ESR)


def get_latest_build(candidate):
    result = request.urlopen(ROOT_URL + candidate + "-candidates/")
    if result.getcode() != HTTPStatus.OK:
        logging.error("failed to fetch the list of builds for {}"
                      .format(candidate))
        return 0
    builds = lxml.html.fromstring(result.read())
    builds = builds.xpath("//a[contains(@href,'-candidates/build')]/text()")
    builds.sort()
    return int(builds[-1][:-1].split('build')[-1])


def test_version(current_version, candidate):
    # Drop the "esr" suffix from the candidate, since version.parse
    # only supports versions that follow the PEP 440 requirements.
    nv = version.parse(candidate.split("esr")[0])
    # Drop the potential build number suffix, as well as the "esr"
    # suffix for the exact reasons as above.
    cv = version.parse(current_version.split('-')[0].split("esr")[0])
    if nv >= cv:
        build = get_latest_build(candidate)
        # Only try to get the build number if it's actually present.
        new_build = "-" in current_version and \
            build > int(current_version.split('-')[1])
        if nv > cv or new_build:
            return '{}-{}'.format(candidate, build)
    return None


def check_new_candidates(channel, current_version):
    new_version = current_version
    result = request.urlopen(ROOT_URL)
    if result.getcode() != HTTPStatus.OK:
        sys.exit("failed to fetch list of candidates")
    candidates = lxml.html.fromstring(result.read())
    candidates = candidates.xpath("//a[contains(@href,'-candidates/')]/text()")
    candidates = [c[:-12] for c in candidates if not c.startswith("None")]
    for candidate in candidates:
        if channel == BETA and "b" not in candidate:
            continue
        if channel == ESR and not candidate.endswith("esr"):
            continue
        if channel == RELEASE and \
           ("b" in candidate or candidate.endswith("esr")):
            continue
        new_version = test_version(new_version, candidate) or new_version
    if new_version != current_version:
        logging.info("new version: {} > {}"
                     .format(new_version, current_version))
        print(new_version)


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    if len(sys.argv) != 3:
        logging.error("Usage: {program} channel current_version"
                      .format(program=sys.argv[0]))
        sys.exit(1)
    assert sys.argv[1] in CHANNELS
    check_new_candidates(*sys.argv[1:])
