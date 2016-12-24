#!/bin/bash
#
# Backup system on remote server using dd.
# 
set -e
set -u
set -o pipefail


if [[ $# != 2 ]]; then
  echo "wrong number of arguments!"
  exit 1
elif [[ $EUID != 0 ]]; then
  echo "you must be root to run this script!"
  exit 1
fi 

remote_user="egx"
remote_server="$2"
date="$(date +%Y-%m-%d)"
distro="$1"
remote_backup_folder="/mnt/storage/backups/dd/${distro}-${date}"

# Activate volume group
echo "Activating volume group ..."
vgchange -ay

# Make remote directory
echo "Creating remote directory ..."
ssh "${remote_user}@${remote_server}" "mkdir -p ${remote_backup_folder}"

# Create backup
echo "Starting backup ..."
dd if=/dev/sda bs=1M status=progress \
  | gzip -c9 \
  | ssh "${remote_user}@${remote_server}" \
  "dd of=${remote_backup_folder}/system.img.gz bs=1M"
