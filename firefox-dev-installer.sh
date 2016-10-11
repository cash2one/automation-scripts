#!/bin/bash
#
# A script to automate per-user installation of firefox developer edition. The
# script will install into ~/.opt and create a symlink of the firefox binary
# into ~/.local/bin plus a .desktop file in .local/share. The script is written
# to be easy adaptable to other self-contained downloaded applications.
#
set -e
set -u
set -o pipefail

source ./bash_functions.sh


# System directories
readonly install_dir="${HOME}/.opt"
readonly launcher_dir="${HOME}/.local/share/applications"
readonly binary_dir="${HOME}/.local/bin"


rollback() {
  local app_name="$1"

  rm -rf "${install_dir:?}/${app_name}" \
    "${launcher_dir:?}/${app_name}.desktop" \
    "${binary_dir:?}/${app_name}"
}


install() {
  local app_url="$1"
  local app_name="$2"

  mkdir -p "${install_dir}/${app_name}"
  echo "installing, please wait ..."
  wget -qO - "${app_url}" \
    | tar --directory="${install_dir}/${app_name}" \
      --extract \
      --preserve-permissions \
      --bzip2 \
      --strip-components=1
}


create_launcher() {
  local app_name="$1"
  local app_exec="$2"
  local app_icon="$3"

  echo "creating launcher ..."
  cat << EOF > "${launcher_dir}/${app_name}.desktop"
[Desktop Entry]
Type=Application
Name=Firefox-dev
Exec=${app_exec}
Icon=${app_icon}
StartupNotify=true
EOF

  echo "creating binary link ..."
  ln -fs "${app_exec}" "${binary_dir}/${app_name}"
}


main() {
  local application="firefox-dev"
  local binary="${install_dir}/${application}/firefox"
  local icon="${install_dir}/${application}/browser/icons/mozicon128.png"
  local url="https://download.mozilla.org/\
    ?product=firefox-aurora-latest-ssl&os=linux64&lang=en-US"

  trap 'rollback ${application}' SIGINT

  # Fail gracefully if a directory with the same name already exists
  if [[ -d "${install_dir}/${application}" ]]; then
    echo "Application seems to be already installed!" >&2 ; exit
  fi

  check_connection www.mozilla.org
  install "${url}" "${application}"
  create_launcher "${application}" "${binary}" "${icon}"
}


main "$@"
