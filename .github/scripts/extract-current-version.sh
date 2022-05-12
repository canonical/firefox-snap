#!/bin/sh
version=$(sed -n 's/^version: "\(.*\)"$/\1/p' snapcraft.yaml)
echo "::set-output name=version::$version"
