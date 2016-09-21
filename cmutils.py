"""
This module provides a series of custom-made classes and functions that
could be useful in some situations:
    Downloader -> A class providing a download percentage progress

    Alzaimer -> A class to remember and restore ownership and permission for
                files and directories inside a given path

    recursive_chown -> A function to recursive change a directory ownership

    recursive_chmod -> A function to recursive change permissions for files and
                       directories inside a given path.
"""

from __future__ import unicode_literals

import itertools
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
        Download the file located at the given url and save it as
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


class PermissionsSnapshot(object):
    """
    Remember and restore ownership and permissions for files and
    directories inside a given path.
    """
    def __init__(self, directory):
        self.directory = directory
        self.snapshot = self.create_snapshot()

    @staticmethod
    def getinfo(path):
        info = os.stat(path)
        mode, uid, gid = info[0], info[4], info[5]
        return mode, uid, gid

    def create_snapshot(self):
        """
        Return a dictionary in which each key is a file path and each
        value is a 3 element tuple in which the elements are: the file
        mode, the uid, and the gid.
        """
        snapshot = {}
        snapshot[self.directory] = self.getinfo(self.directory)
        for dirpath, dirnames, filenames in os.walk(self.directory):
            for i in itertools.chain(dirnames, filenames):
                i_path = os.path.join(dirpath, i)
                snapshot[i_path] = self.getinfo(i_path)
        return snapshot

    def restore(self):
        """Restore permissions stored in the snapshot."""
        for path, info in self.snapshot.iteritems():
            os.chmod(path, info[0])
            os.chown(path, info[1], info[2])


def recursive_chown(basedir, uid, gid):
    """Mimicks shell chown -R."""
    os.chown(basedir, uid, gid)
    for dirpath, dirnames, filenames in os.walk(basedir):
        for i in itertools.chain(dirnames, filenames):
            i_path = os.path.join(dirpath, i)
            os.chown(i_path, uid, gid)


def recursive_chmod(basedir, directory_mode, file_mode):
    """Change files and directory permissions recursively."""
    os.chmod(basedir, directory_mode)
    for dirpath, dirnames, filenames in os.walk(basedir):
        for dirname in dirnames:
            os.chmod(os.path.join(dirpath, dirname), directory_mode)
        for filename in filenames:
            os.chmod(os.path.join(dirpath, filename), file_mode)
