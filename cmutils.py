"""
This module provides a series of custom-made classes and functions that
could be useful in some situations:
    Downloader -> A class providing a download percentage progress
    recursive_chown -> A function to recursive change a directory ownership
"""

from __future__ import unicode_literals

import os
import sys
import urllib2


class Downloader(object):
    """
    Manage downloads showing a percentage progress. The path of all
    files downloaded by an instance of this class will be saved in the
    "downloaded" attribute.
    """
    def __init__(self):
        self.downloaded = []

    @staticmethod
    def reporthook(blocknumber, blocksize, totalsize):
        """
        Provide a download progress in percentage form. Function takes
        the number of written blocks, the size of each block and the
        total size of the file.
        """
        percentage = (blocknumber*blocksize*100/totalsize)
        sys.stdout.write('\rDownload progress: %2d%%' % percentage)
        sys.stdout.flush()
        if percentage == 100:
            sys.stdout.write('\n')

    def download(self, url, filename):
        """
        Download the file located at the given url as save it as
        "filename". Once the file has been downloaded, add it to the
        list of succesfull downloads.
        """
        source = urllib2.urlopen(url)
        headers = source.info()
        blocknumber = 0
        blocksize = 4096
        totalsize = int(headers["Content-Length"])

        with open(filename, 'w+') as destination:
            while blocknumber*blocksize < totalsize:
                destination.write(source.read(blocksize))
                blocknumber += 1
                self.reporthook(blocknumber, blocksize, totalsize)
        source.close()
        self.downloaded.append(filename)


def recursive_chown(basedir, uid, gid):
    """Mimicks shell chown -R."""
    for dirpath, dirnames, filenames in os.walk(basedir):
        for dirname in dirnames:
            os.chown(os.path.join(dirpath, dirname), uid, gid)
        for filename in filenames:
            os.chown(os.path.join(dirpath, filename), uid, gid)
