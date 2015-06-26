#!/bin/bash -x
set -euo pipefail
IFS=$'\n\t'

#
# 'atomic mount' integration tests (non-live)
# AUTHOR: William Temple <wtemple at redhat dot com>
#

if [[ "$(id -u)" -ne "0" ]]; then
    echo "Atomic mount tests require root access to manipulate devices."
    exit 1
fi

setup () {
    MNT_WORK="${WORK_DIR}/mnt_work"
    mkdir -p "${MNT_WORK}"
    mkdir -p "${MNT_WORK}/container"
    mkdir -p "${MNT_WORK}/image"

    INAME=${INAME:-"atomic_mount_test"}

    CHECKSUM=`dd if=/dev/urandom bs=4096 count=1 2> /dev/null  | sha256sum`
    echo -n "${CHECKSUM}" > "${MNT_WORK}/val"
}

teardown () {
    rm -rf "${MNT_WORK}"
}
trap teardown EXIT

setup

cat > "${MNT_WORK}/Dockerfile" << EOF
FROM scratch
ADD ./val /val
EOF

${DOCKER} build -t ${INAME} ${MNT_WORK}

cleanup_image () {
    "${DOCKER}" rmi ${INAME}
    teardown
}
trap cleanup_image EXIT

id=`${DOCKER} create ${INAME} /bin/true`

cleanup_container () {
    ${DOCKER} rm ${id}
    cleanup_image
}
trap cleanup_container EXIT

./atomic mount ${id} ${MNT_WORK}/container
./atomic mount ${INAME} ${MNT_WORK}/image

# Expect failure
set +e
./atomic mount ${id} --live ${MNT_WORK}/container
if [ "$?" -eq "0" ]; then
    exit 1
fi
./atomic mount ${INAME} --live ${MNT_WORK}/image
if [ "$?" -eq "0" ]; then
    exit 1
fi
set -e

cleanup_mount () {
    ./atomic unmount ${MNT_WORK}/container
    ./atomic unmount ${MNT_WORK}/image
    cleanup_container
}
trap cleanup_mount EXIT

if [[ "`cat "${MNT_WORK}/container/val"`" !=  "${CHECKSUM}" ]]; then
    exit 1
fi
if [[ "`cat "${MNT_WORK}/image/val"`" != "${CHECKSUM}" ]]; then
    exit 1
fi
