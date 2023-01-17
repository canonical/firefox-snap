#!/bin/sh

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
