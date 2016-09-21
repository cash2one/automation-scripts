#!/usr/bin/env python
"""
This script will harden the given wordpress installation. If you have
SElinux enabled with default settings, you will NOT be able to:

    * Install, remove or update plugins and themes from web interface,
    unless you install the "ssh sftp updater support" plugin and enable
    SElinux boolean httpd_can_network_connect;

    * Use ftp client to manage content: this is because if you are using
    ftp, you are running on the system as ftp user, and not as your own
    user account. As an alternative you can use sftp protocol.
"""

from __future__ import print_function, unicode_literals

import argparse
import os
import signal
import sys

from cmutils import recursive_chown, recursive_chmod, PermissionsSnapshot


def sigint_handler(signum, handler):
    """Ignore sigint to avoid user interruption."""
    pass


def let_apache_write(basedir):
    uid = os.stat(basedir).st_uid
    recursive_chown(basedir, uid, 48)
    recursive_chmod(basedir, 0o775, 0o664)


def get_args():
    """Parse and return arguments passed to the script."""
    parser = argparse.ArgumentParser()
    parser.add_argument('path', help='The path to the site root directory')

    parser.add_argument(
        'uid',
        help='The uid of the user who should own site directory and files',
        type=int
    )

    parser.add_argument(
        '-t', '--themes-access',
        action='store_true',
        dest='allow_themes',
        help='Allow changing themes from built-in wordpress theme editor'
    )

    parser.add_argument(
        '-p', '--plugins-access',
        action='store_true',
        dest='allow_plugins',
        help='Allow modifications of plugins code from web interface'
    )

    args = parser.parse_args()
    return args.path, args.uid, args.allow_themes, args.allow_plugins


def main():
    signal.signal(signal.SIGINT, sigint_handler)
    site_path, owner_uid, themes_access, plugins_access = get_args()

    if os.geteuid() != 0:
        print('You must be root to run this script!')
        sys.exit(1)

    # Wordpress directories path, relative to site directory
    wp_content_directory = os.path.join(site_path, 'wp-content')
    wp_themes_directory = os.path.join(wp_content_directory, 'themes')
    wp_plugins_directory = os.path.join(wp_content_directory, 'plugins')

    # Create a snapshot of the directory permission, to allow an easy rollback
    original_setup = PermissionsSnapshot(site_path)

    # The root wordpress directory: all files should be writeable only by your
    # user account, except .htaccess if you want wordpress to automatically
    # generate rewrite rules for you.
    print('Recursively change site ownership to user %s...' % owner_uid)
    try:
        recursive_chown(site_path, owner_uid, owner_uid)
        recursive_chmod(site_path, 0o755, 0o644)
    except OSError as permission_error:
        sys.exit(permission_error.strerror, file=sys.stderr)

    # /wp-content
    # -----------
    # user-supplied content. Intended to be writable by your user account and
    # the web server process.
    print('applying settings for wp-content directory...')
    try:
        os.chown(wp_content_directory, owner_uid, 48)
        os.chmod(wp_content_directory, 0o775)
    except OSError as wpcontent_error:
        print(wpcontent_error.strerror, file=sys.stderr)
        original_setup.restore()
        sys.exit(1)

    # /wp-content/themes
    # ------------------
    # if you want to use the build-in theme editor, all files need to be
    # writable by the webserver process.
    if themes_access:
        print('applying wp-content/themes directory settings...')
        try:
            let_apache_write(wp_themes_directory)
        except OSError as themes_error:
            print(themes_error.strerror, file=sys.stderr)
            original_setup.restore()
            sys.exit(1)

    # /wp-content/plugins
    # -------------------
    # all files should be writable only by your user account. However if this
    # option is passed the plugins code will be accessible and customizable
    # from the web interface
    if plugins_access:
        print('applying wp-content/plugins directory settings...')
        try:
            let_apache_write(wp_plugins_directory)
        except OSError as plugins_error:
            print(plugins_error.strerror, file=sys.stderr)
            original_setup.restore()
            sys.exit(1)


if __name__ == '__main__':
    main()
