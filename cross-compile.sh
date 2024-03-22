#!/bin/sh

ARCH=${ARCH:-amd64}

# This will create and start an instance. You are responsible for performing a
# 'snap run snapcraft clean' step
snap run snapcraft --build-for=${ARCH} --verbosity verbose --use-lxd
rv=$?

if [ "${rv}" -ne "1" ]; then
  echo "Happy happy person."
  exit 0
fi;

INSTANCE=$(lxc list --project snapcraft --columns "n" --format "compact" | grep firefox-on-amd64-for-${ARCH})
NB=$(echo ${INSTANCE} | wc -l)
if [ "${NB}" -ne "1" ]; then
  echo "Clean instances please."
  exit 1;
fi;

lxc start --project snapcraft ${INSTANCE}

lxc exec --project snapcraft ${INSTANCE} -- dpkg --add-architecture ${ARCH}
lxc exec --project snapcraft ${INSTANCE} -- sed -ri "s/^deb /deb [arch=amd64] /g" /etc/apt/sources.list
lxc exec --project snapcraft ${INSTANCE} -- apt update
lxc exec --project snapcraft ${INSTANCE} -- apt --fix-broken install -y
lxc exec --project snapcraft ${INSTANCE} -- apt upgrade -y

lxc stop --project snapcraft ${INSTANCE}

snap run snapcraft --build-for=${ARCH} --verbosity verbose --use-lxd
