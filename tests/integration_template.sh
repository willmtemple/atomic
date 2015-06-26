#!/bin/bash -x
set -euo pipefail
IFS = $'\n\t'

# Above sets 'Bash Unofficial Strict Mode'. This mode can be quite onerous
# to seasoned bash programmers who are used to bash's more forgiving
# features, but will save time and code quality debugging overall. Compare
# to `gcc -Wall -Wextra -Werror`. For information about common pitfalls:
#   http://redsymbol.net/articles/unofficial-bash-strict-mode/

# The test harness exports several variables into the environment during
# testing.

setup () {
    # Perform setup routines here.
    true
}

teardown () {
    # Cleanup your test data.
    true
}
# Utilize exit traps for cleanup wherever possible. Additional cleanup
# code can be added by creating another function which calls cleanup, and
# then replacing the exit trap with that function instead. See
# tests/integration/test_mount.sh for an example.
trap teardown EXIT

# The test is considered to pass if it exits with zero status. Any other
# exit status is considered failure.

OUTPUT=$(/bin/true)

if [[ "$?" -ne "0" ]]; then
    exit 1
fi
