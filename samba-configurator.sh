#!/bin/bash
#
# Samba installer and configurator for CentOS7. This script will manage
# everything is needed to have samba up and running: it will install
# packages, add share to samba configuration, setup selinux booleans
# (for samba in read only mode), add appropriate selinux target label
# on shared directory and files, and add "samba" service to the selected
# firewalld zone (by default is the "home" zone, change it as you like).
#
set -e
set -u
set -o pipefail

# The directory to be shared
readonly shared_dir="/mnt/storage/shared"


packages_install() {
  local packages="samba policycoreutils-python"
  local package
  for package in ${packages}; do
    echo "Installing ${package} ... "
    yum install -y "${package}" > /dev/null
  done
}


add_share() {
  if ! grep "${shared_dir}" /etc/samba/smb.conf; then
    echo "Backing up original configuration ... "
    cp /etc/samba/smb.conf /etc/samba/smb.conf.orig
    echo "Writing share information in /etc/samba/smb.conf ... "
    cat << EOF >> /etc/samba/smb.conf

[shared]
path = "${shared_dir}"
browseable = yes
writeable = no

EOF
  else
    echo "Shared directory already exists in /etc/samba/smb.conf ... "
    return 1
  fi
}


create_user() {
  # Create user for samba with no real shell and nome home directory, and add
  # it to the samba database
  echo "Creating user ... "
  useradd -M -s /bin/false smbuser
  smbpasswd -a smbuser
}


selinux_setup() {
  echo "enabling selinux boolean (samba_export_all_ro) ... "
  setsebool samba_export_all_ro 1 
  echo "Creating and applying SElinux context for shared directory ... "
  semanage fcontext -a -t samba_share_t "${shared_dir}(/.*)?"
  restorecon -R $shared_dir
}


firewall_setup() {
  local zone=home
  if systemctl -q is-active firewalld; then
    echo "Permanenty adding samba service to firewall zone (${zone}) ..."
    firewall-cmd -q --permanent --zone="${zone}" --add-service=samba
    firewall-cmd -q --reload
  else
    echo "firewalld is not active, skipping ..."
  fi
}


service_start() {
  local services="smb nmb"
  local service
  for service in ${services}; do
    echo "Starting and enabling ${service} ... "
    systemctl -q enable --now "${service}"
  done
}


main() {
  if [[ $UID -ne 0 ]]; then
    echo "You need root privileges to run this script"
    exit 1
  elif [[ ! -d ${shared_dir} ]]; then
    echo "Shared directory doesn't exists, aborting ..."
    exit 1
  fi

  packages_install
  add_share
  create_user
  selinux_setup
  firewall_setup
  service_start
}


main "$@"
