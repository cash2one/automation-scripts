"""
Call this script with the system main python executable: all python
packages will be installed with pip, according to it.
"""
from __future__ import print_function, unicode_literals

import os
import subprocess
import sys

try:
    import pip
except ImportError:
    print('You should install pip!')
    sys.exit(1)


def git_clone(address, destination):
    """
    Clone a git repository at the given destination. The repository name
    will be 'extracted' from the last part of the repository url.
    """
    repo_name = address.split('/')[-1]
    repo_directory = os.path.join(destination, repo_name)
    cmd = ['git', 'clone', '-q', '--recursive', address, repo_directory]
    subprocess.check_call(cmd)


def stow(stow_root, package):
    """
    Stow 'package' in 'stow_root' considering the user home directory as
    target (read gnu stow manual for futher informations).
    """
    home = os.getenv('HOME')
    if package == 'bash':
        targets = [os.path.join(home, i) for i in ['.bashrc', '.bash_profile']]
        for i in targets:
            os.rename(i, i + '.orig')
    cmd = ['stow', '-d', stow_root, '-t', home, package]
    subprocess.check_call(cmd)


def main():
    py_packages = ['flake8', 'virtualenv', 'youtube-dl', 'pylint']
    stow_packages = ['vim', 'wallpapers', 'fonts', 'bash', 'pylint']

    git_directory = (os.path.join(os.getenv('HOME'), 'git'))
    git_repos = [
        'https://github.com/egdoc/dotfiles',
        'https://github.com/egdoc/init',
        'https://github.com/egdoc/phs'
    ]

    # if i3wm is installed we need to stow some other packages
    if os.path.exists('/usr/bin/i3'):
        stow_packages.extend(['i3', 'xorg', 'mutt'])

    for repo in git_repos:
        try:
            print('starting to clone %s...' % repo)
            git_clone(repo, git_directory)
        except subprocess.CalledProcessError:
            pass

    for stow_package in stow_packages:
        try:
            print('stowing %s...' % stow_package)
            stow(os.path.join(os.getenv('HOME'), 'git/dotfiles'), stow_package)
        except subprocess.CalledProcessError:
            pass

    for package in py_packages:
        pip.main(['install', '--disable-pip-version-check', package, '--user'])

    try:
        print('reloading fonts cache...')
        subprocess.check_call(['fc-cache', '-f'])
    except subprocess.CalledProcessError:
        pass

if __name__ == '__main__':
    main()
