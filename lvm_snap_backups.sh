#!/bin/bash 
#
# This script uses the lvm snapshot feature to create backups of the specified
# logical volumes. First snapshot of the lv is created, than it's content is
# backed up with dd to a directory inside the specified location. The full
# destination path will be composed this way: location/distro_name/date
# Once the backup is done the snapshot will be removed
#
set -e
set -u
set -o pipefail

dd_backup() {
  src=$1
  destination=$2
  dd if="${src}" bs=1M status=progress | gzip -c9 | dd of="${destination}"
}

main() {

  if [[ "$#" -ne 1 ]]; then
    echo "Incorrect number of arguments!"
    exit 1
  elif [[ "$EUID" -ne 0 ]]; then
    echo "You must be root to run this script!"
    exit 1
  fi 

  logical_volumes="root_lv home_lv"
  date="$(date +%Y-%m-%d)"
  distribution="$(cat /etc/redhat-release | cut -f1 -d " ")"
  destination=$1
  path="${destination}/${distribution}/${date}"
  
  mkdir -p "${path}"

  for lv in ${logical_volumes}; do
    echo "creating logical volume snapshot for ${lv} ..."
    lvm lvcreate -l +100%FREE -s -n "${lv}_snapshot" "/dev/fingolfin_vg/${lv}"
    
    # Use dd and gzip to create a clone of the snapshot
    echo "cloning into ${path}"
    dd_backup "/dev/fingolfin_vg/${lv}_snapshot" "${path}/${lv}.dd.gz"
    
    # Remove the snapshot logical volume
    lvm lvremove -f --no-history "/dev/fingolfin_vg/${lv}_snapshot"
  done
}

main "$@"
