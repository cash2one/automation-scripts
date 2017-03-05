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

for binary in ['stow', 'git']:
    try:
        subprocess.Popen([binary], stdout=subprocess.PIPE)
    except FileNotFoundError:
        sys.exit('Missing dependency: %s' % binary)


def git_clone(address, destination):
    """
    Clone a git repository into the given destination. The repository
    name will be 'extracted' from the last part of the repository url.
    """
    repo_name = address.split('/')[-1]
    repo_directory = os.path.join(destination, repo_name)
    cmd = ['git', 'clone', '-q', '--recursive', address, repo_directory]
    subprocess.check_call(cmd)


def stow(stow_root, package):
    """
    Stow 'package' contained in 'stow_root', considering the user home
    directory as target (read gnu stow manual for futher informations).
    """
    home = os.getenv('HOME')
    if package == 'bash':
        targets = [os.path.join(home, i) for i in ['.bashrc', '.bash_profile']]
        for i in targets:
            try:
                os.rename(i, i + '.orig')
            except OSError:
                pass
    cmd = ['stow', '-d', stow_root, '-t', home, package]
    subprocess.check_call(cmd)


def main():
    py_packages = ['flake8', 'virtualenv', 'pylint']
    stow_packages = ['vim', 'bash', 'pylint', 'wallpapers']

    # if i3wm is installed we need to stow some other packages
    if os.path.exists('/usr/bin/i3'):
        stow_packages.extend(['i3', 'xorg', 'mutt'])

    git_directory = (os.path.join(os.getenv('HOME'), 'git'))
    git_repos = [
        ('https://github.com/egdoc/dotfiles', git_directory),
        ('https://github.com/egdoc/init', git_directory),
        ('https://github.com/egdoc/powerline/fonts', git_directory),
        ('https://github.com/egdoc/kickstart', git_directory),
        ('https://github.com/egdoc/lamp-dockerfile', git_directory),
        ('https://github.com/egdoc/phs', git_directory),
        ('https://gitlab.com/egdoc/fantapilu', git_directory)
    ]

    # Clone git repositories
    for repo, destination in git_repos:
        print('starting to clone %s...' % repo)
        try:
            git_clone(repo, destination)
        except subprocess.CalledProcessError:
            pass

    # Place dotfiles with gnu stow
    for stow_package in stow_packages:
        print('stowing %s...' % stow_package)
        try:
            stow(os.path.join(os.getenv('HOME'), 'git/dotfiles'), stow_package)
        except subprocess.CalledProcessError:
            pass

    # Install python packages with pip
    for package in py_packages:
        pip.main(['install', '--disable-pip-version-check', package, '--user'])

    # Remove bash backup files if present
    for i in ['.bashrc.orig', '.bash_profile.orig']:
        try:
            os.remove(os.path.join(os.getenv('HOME'), i))
        except FileNotFoundError:
            pass
        else:
            print('Removed %s' % i)


if __name__ == '__main__':
    main()
