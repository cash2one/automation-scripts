### firefox-dev-installer
A script to automate the installation of firefox-developer-edition.
It will install the application in ~/.opt, link the binary in ~/.local/bin
and create a .desktop launcher in ~/.local/share/applications


### samba-configurator
Samba installer and configurator for CentOS7. This script will manage
everything is needed to have samba up and running: it will install
packages, add share to samba configuration, setup selinux booleans
(for samba in read only mode), add appropriate selinux target label
on shared directory and files, and add "samba" service to the selected
firewalld zone (by default is the "home" zone, change it as you like).


### wp_deploy
A python script meant to automate the creation of a basic wordpress site.
The script will download the latest wordpress tarball from wordpress.org,
create the site directory in /var/www/html, and create a basic apache
VirtualHost file. Script help:

Usage: wpdeploy.py [-h] [--ip IP] url

positional arguments:

    url:         the site url

optional arguments:

    -h, --help  show this help message and exit

    --ip IP     use an IP based VirtualHost
  
  
### workstastion_setup
A python script meant to automate some tasks after system installation, like the
cloning of some git repositories and the placing of dotfiles. You should run it
with your system main python version. All python applications will be installed
accordingly with pip.

