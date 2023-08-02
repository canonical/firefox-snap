#!/bin/sh
version=$(sed -n 's/^version: "\(.*\)"$/\1/p' snapcraft.yaml)
echo "current_version=$version" >> $GITHUB_ENV
