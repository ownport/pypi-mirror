#!/usr/bin/env python
#
#   pypi-mirror
#

import os
import re
import pip
import sys
import shutil
import logging
import pkg_resources


logging.basicConfig(name=__name__, format='%(asctime)s [%(levelname)s] %(message)s')


class PyPIMirror(object):

    def __init__(self, packages_list, directory, pip_log_file=None):

        if not packages_list or not os.path.exists(packages_list):
            raise RuntimeError('The packages list does not exists, %s' % packages_list)

        if not directory or not os.path.exists(directory):
            raise RuntimeError('The directory for packages does not exists, %s' % directory)

        self._pip_log_file = None
        if pip_log_file:
            self._pip_log_file = pip_log_file

        self._packages = packages_list
        self._packages_dir = os.path.join(directory, 'packages/')
        self._index_dir = os.path.join(directory, 'simple/')

        if not os.path.exists(self._packages_dir):
            os.mkdir(self._packages_dir)

        if os.path.exists(self._index_dir):
            shutil.rmtree(self._index_dir)
        os.mkdir(self._index_dir)


    def update(self):

        self.update_packages()
        self.update_index()


    def update_packages(self):

        with open(self._packages, 'r') as _packages:
            for _package in _packages:
                _package = _package.strip()
                if _package:
                    cmd = ['install', '-q', '--download', self._packages_dir]
                    if self._pip_log_file:
                        cmd.extend(['--log-file', self._pip_log_file])
                    cmd.append(_package.strip())
                    pip.main(cmd)


    def update_index(self):

        packages = [(f, self.pypi_package(f), os.path.join(self._packages_dir, f)) \
                        for f in os.listdir(self._packages_dir) 
                            if os.path.isfile(os.path.join(self._packages_dir, f)) and not f.startswith(".")]

        for _file, _package, path in packages:

            full_pkg_path = os.path.join(self._index_dir, _package.lower())
            if not os.path.isdir(full_pkg_path):
                os.mkdir(full_pkg_path)

            # print (_file, _package), os.path.join(self._index_dir, _package, _file), path
            logging.info(_file)
            os.symlink(
                os.path.join('../../packages/', _file), 
                os.path.join(self._index_dir, _package, _file)
            )


    def pypi_package(self, file):
        """ Returns the package name for a given file, or 
            raises an RuntimeError exception if the file name is not valid
            """

        file = os.path.basename(file)
        file_ext = os.path.splitext(file)[1].lower()

        if file_ext == ".egg":
            dist = pkg_resources.Distribution.from_location(None, file)
            name = dist.project_name
            split = (name, file[len(name)+1:])
            to_safe_name = lambda x: x
        
        if file_ext == ".whl":
            bits = file.rsplit("-", 4)
            split = (bits[0], "-".join(bits[1:]))
            to_safe_name = pkg_resources.safe_name
        else:
            match = re.search(r"(?P<pkg>.*?)-(?P<rest>\d+.*)", file)
            if not match:
                raise RuntimeError('[ERROR] Invalid package name, %s' & file)
            split = (match.group("pkg"), match.group("rest"))
            to_safe_name = pkg_resources.safe_name

        if len(split) != 2 or not split[1]:
            raise RuntimeError('[ERROR] Invalid package name, %s' & file)

        return to_safe_name(split[0]).lower()


if __name__ == '__main__':

    import optparse

    parser = optparse.OptionParser()
    parser.add_option('-d', '--directory', help='path to py-packages')
    parser.add_option('-p', '--packages', help='packages list')
    parser.add_option('-l', '--pip-log-file', help='pip log file')
    (opts, args) = parser.parse_args()

    try:
        mirror = PyPIMirror(opts.packages, opts.directory, opts.pip_log_file)
        mirror.update()
    except Exception, err:
        logging.error(err)