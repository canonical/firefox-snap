#!/bin/sh

# Copyright (C) 2023 Canonical Ltd.
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

if [ $# -ne 1 ]; then
    echo "Usage: $0 <current_version>"
    exit 1
fi

current_version="$1"

firefox_versions="https://product-details.mozilla.org/1.0/firefox_versions.json"
new_version=$(curl -s "${firefox_versions}" | jq -r '.FIREFOX_NIGHTLY')

if dpkg --compare-versions "${current_version}" lt "${new_version}"; then
    echo "new_version=${new_version}" >> $GITHUB_ENV
fi
