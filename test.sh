#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

#
# Test harness for the atomic CLI.
#
export PYTHONPATH=${PYTHONPATH:-$(pwd)}
export WORK_DIR=$(mktemp -p $(pwd) -d -t .tmp.XXXXXXXXXX)
export DOCKER=${DOCKER:-"/usr/bin/docker"}

LOG=${LOG:-"$(pwd)/tests.log"}

echo -n '' > ${LOG}

cleanup () {
    rm -rf ${WORK_DIR}
}
trap cleanup EXIT

# Python unit tests.
echo "UNIT TESTS:"

COVERAGE="/usr/bin/coverage"
if [[ ! -x "${COVERAGE}" ]]; then
    COVERAGE="/usr/bin/coverage2"
fi

set +e

${COVERAGE} run --source=./Atomic/ --branch  -m unittest discover \
	./tests/unit | tee -a ${LOG}

if [[ "$?" -ne "0" ]]; then
    echo "Some unit tests failed."
fi
set -e

echo "Coverage report:" | tee -a ${LOG}

${COVERAGE} report | tee -a ${LOG}
${COVERAGE} html

# CLI integration tests.
let failures=0 || true
printf "\nINTEGRATION TESTS:\n" | tee -a ${LOG}

for tf in `find ./tests/integration/ -name test_*.sh`; do
    printf "Running test ${tf}...\t\t"
    printf "\n==== ${tf} ====\n" >> ${LOG}
    if ${tf} &>> ${LOG}; then
        printf "PASS\n";
    else
        printf "FAIL\n";
        let "failures += 1"
    fi
done

if [[ "${failures}" -eq "0" ]]; then
    echo "ALL TESTS PASSED"
    exit 0
else
    echo "Failures: ${failures}"
    echo "See ${LOG} for more information."
    exit 1
fi
