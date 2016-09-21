#!/usr/bin/env python2
"""
Script to fast deploy a wordpress installation. It will create the site
directory, install wordpress in it and change its ownership to apache
(you should change this after setup). The script will refuse to override
an existing site directory or VirtualHost file.
"""

from __future__ import print_function, unicode_literals

import argparse
import os
import shutil
import subprocess as sp
import sys
import textwrap

from cmutils import Downloader, recursive_chown


class WpSite(object):
    """
    Manage the creation of a wordpress site and of the corresponding
    apache VirtualHost configuration. An instance of this class should
    be initialized with the site url as argument. If the 'host_ip'
    argument is passed, will generate an ip-based VirtualHost file based
    on the given address.
    """
    def __init__(self, url, host_ip=None):
        self.url = url
        self.host_ip = host_ip
        self.name = url.split('.')[-2]
        self.base = os.path.join('/var/www/html', self.name)
        self.vhost = '/etc/httpd/conf.d/vhost-%s.conf' % self.name

    def virtualhost_setup(self):
        """Generate the site VirtualHost configuration."""
        os.mkdir(self.base)
        config = textwrap.dedent(
            """\
            <VirtualHost %s:80>
                ServerName %s
                DocumentRoot "%s"
            </VirtualHost>\n\n
            """ % (self.host_ip if self.host_ip else '*', self.url, self.base)
        )

        # This will raise an exception if file already exists (python3 has the
        # much nicer 'x' mode when using open(), but python2 is default on rhel
        desc = os.open(self.vhost, os.O_CREAT | os.O_WRONLY | os.O_EXCL, 0o644)
        with os.fdopen(desc, 'w') as virtualhost:
            virtualhost.write(config)

    def install(self, source):
        cmd = ['tar', '-C', self.base, '-xf', source, '--strip-components=1']
        sp.check_call(cmd)
        recursive_chown(self.base, 48, 48)

    def rollback(self):
        shutil.rmtree(self.base)
        os.remove(self.vhost)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('url', help='the site url')
    parser.add_argument('--ip', dest='ip', help='use an IP based VirtualHost')
    args = parser.parse_args()

    site_url = args.url
    site_host_ip = args.ip
    wp_tarball = '/var/tmp/latest-wordpress.tar.gz'

    try:
        site = WpSite(site_url, site_host_ip)
    except IndexError:
        print('you should provide at least a second level domain name!')
        sys.exit(1)

    # Setting up VirtualHost file and site directory
    print('setting up VirtualHost...', end='')
    try:
        site.virtualhost_setup()
    except OSError as virtualhost_error:
        print(virtualhost_error)
        sys.exit(1)
    else:
        print('done!')

    # Download wordpress tarball
    print('starting wordpress tarball download...')
    try:
        downloader = Downloader()
        downloader.download('https://wordpress.org/latest.tar.gz', wp_tarball)
    except (IOError, KeyboardInterrupt):
        print('failed!')
        site.rollback()
        os.remove(wp_tarball)
        sys.exit(1)

    # Install wordpress
    print('installing wordpress...', end='')
    try:
        site.install(wp_tarball)
    except (sp.CalledProcessError, KeyboardInterrupt):
        site.rollback()
        os.remove(wp_tarball)
        sys.exit(1)
    else:
        print('done!')
    finally:
        os.remove(wp_tarball)

    # Reload httpd server
    print('reloading httpd...', end='')
    try:
        sp.check_call(['systemctl', 'reload', 'httpd'])
    except sp.CalledProcessError:
        pass
    else:
        print('done!')


if __name__ == '__main__':
    main()
