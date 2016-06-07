#!/usr/bin/env python
#
#   pypi-mirror
#

import os
import re
import pip
import sys
import json
import shutil
import pkg_resources

__version__ = "1.1.0"

RE_PACKAGE_NAME=re.compile(r"(?P<pkg>.*?)-(?P<rest>\d+.*)")


class PyPIMirror(object):

    def __init__(self, packages_list, directory, verbose=False, pip_log=None):

        if not packages_list or not os.path.exists(packages_list):
            raise RuntimeError('The packages list does not exists, %s' % packages_list)

        if not directory or not os.path.exists(directory):
            raise RuntimeError('The directory for packages does not exists, %s' % directory)

        self._pip_log = None
        if pip_log:
            self._pip_log = pip_log

        self._verbose = verbose
        if not isinstance(verbose, bool):
            self._verbose = False

        self._packages = packages_list
        self._packages_dir = os.path.join(directory, 'packages/')
        self._index_dir = os.path.join(directory, 'simple/')

        if not os.path.exists(self._packages_dir):
            os.mkdir(self._packages_dir)

        if os.path.exists(self._index_dir):
            shutil.rmtree(self._index_dir)
        os.mkdir(self._index_dir)

        self._py_version = "py%s" % sys.version_info[0]


    def update(self):

        self.update_packages()
        self.update_index()


    def update_packages(self):

        base_cmd = ['download',]
        if not self._verbose:
            base_cmd.append('-q')
        base_cmd.extend(["--dest", self._packages_dir])
        if self._pip_log:
            base_cmd.extend(['--log', self._pip_log])

        with open(self._packages, 'r') as _packages:
            for pkg in _packages:
                print
                try:
                    _package = json.loads(pkg)
                    if self._py_version not in _package.get("env", []):
                        continue
                    cmd = list()
                    cmd.extend(base_cmd)
                    cmd.append(_package["name"].strip())
                    pip.main(cmd)
                except:
                    pass


    def update_index(self):

        packages = [(f, self.pypi_package(f), os.path.join(self._packages_dir, f)) \
                        for f in os.listdir(self._packages_dir)
                            if os.path.isfile(os.path.join(self._packages_dir, f)) and not f.startswith(".")]

        additional_packages = ([(f, pkg.replace(".", "-"), path) for f, pkg, path in packages if pkg.find('.') > 0])
        packages.extend(additional_packages)

        for _file, _package, path in packages:

            full_pkg_path = os.path.join(self._index_dir, _package.lower())
            if not os.path.isdir(full_pkg_path):
                os.mkdir(full_pkg_path)

            os.symlink(
                os.path.join('../../packages/', _file),
                os.path.join(self._index_dir, _package, _file)
            )


    def pypi_package(self, file):
        """ Returns the package name for a given file, or
            raises an RuntimeError exception if the file name is not valid
            """

        file = os.path.basename(file)
        match = RE_PACKAGE_NAME.search(file)
        if not match:
            raise RuntimeError('[ERROR] Invalid package name, %s' & file)
        split = (match.group("pkg"), match.group("rest"))
        to_safe_name = pkg_resources.safe_name

        if len(split) != 2 or not split[1]:
            raise RuntimeError('[ERROR] Invalid package name, %s' & file)

        return to_safe_name(split[0]).lower()


if __name__ == '__main__':

    import optparse

    parser = optparse.OptionParser(version=__version__)
    parser.add_option('-d', '--directory', help='path to py-packages')
    parser.add_option('-p', '--packages', help='packages list')
    parser.add_option('-l', '--pip-log', help='pip log')
    parser.add_option('-v', '--verbose', action="store_true", help='verbose mode')
    (opts, args) = parser.parse_args()

    if not opts.directory and not opts.packages:
        parser.print_help()
        sys.exit(1)

    mirror = PyPIMirror(opts.packages, opts.directory, opts.verbose, opts.pip_log)
    mirror.update()
