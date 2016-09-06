#!/bin/bash
#
# This file is meant to be sourced from other scripts
#

# Functions to test connection against a given ip or url
check_connection() {
  local test_address="$1"
  echo "testing connection against ${test_address} ..."
  ping -c3 "${test_address}" &> /dev/null \
    || { echo "can't reach ${test_address}!" >&2; return 1; }
}

# Check the presence of given binaries. This is useful to test that all is
# installed before executing a script: fail early!
check_binaries() {
  local binaries="$1"
  local binary

  echo "checking needed binaries ..."
  for binary in ${binaries}; do
    type "${binary}" &> /dev/null \
      || { echo "${binary} not installed!" >&2; return 1; }
  done
}
