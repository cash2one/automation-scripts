#!/bin/bash
#
# Backup system on remote server using dd. The script backups the mbr, the
# space between mbr and the first partition (assumed that it starts sector
# 2048) and the partition 1,2,3 of /dev/sda (images compressed with gzip)
# 
set -e
set -u
set -o pipefail


partition_backup() {
  partition="$1"
  destination="$2"

  dd if=/dev/"${partition}" bs=1M status=progress \
    | gzip -c9 \
    | ssh "${remote_user}@${remote_server}" \
      "dd of=${destination}/${partition}.img.gz"
}

main() {
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
  partitions="sda1 sda2 sda3"

  
  ssh "${remote_user}@${remote_server}" "mkdir -p ${remote_backup_folder}"

  # Create backup of mbr
  dd if=/dev/sda bs=512 count=1 | ssh "${remote_user}@${remote_server}" \
    "dd of=${remote_backup_folder}/mbr.img"
  
  # Create backup of the space between mbr and the first partition 
  dd if=/dev/sda bs=512 count=2047 skip=1 | ssh "${remote_user}@${remote_server}" \
    "dd of=${remote_backup_folder}/after-mbr.img"
  
  for partition in $partitions; do
    partition_backup "${partition}" "${remote_backup_folder}"
  done
}

main "$@"
