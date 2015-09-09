__author__ = 'Panagiotis Koukos'

"""
This is a local repository for most of the code in use by the main programs of
the HERV-K identification pipeline. The aim is for it to be as modular as possible.
Ideally all of the functions/classes should be callable from the terminal and a
script as well.
"""

import os
import subprocess


class Directory(object):
    """
    Models a directory along with a few of its properties.
    Those properties are:
        path: string, The path of the directory.
        contents: list, An alphabetical list of the contents of the directory.
    """

    def __init__(self, path='.'):
        """
        Returns a Directory object whose path is *path*, *contents* are the
        contents of that directory. If it passes the sanity checks that is.

        Paths are always absolute to the filesystem root for consistency. Also
        for consistency, no paths end with a trailing slash. eg: /home/user
        instead of /home/user/
        """
        if not isinstance(path, str):
            raise TypeError('Path should be a string.'
                            ' Instead, path has a type of', type(path),
                            'and a value of', path)

        if not os.path.isdir(path):
            raise RuntimeError('Path either does not point to a directory or does not exist.'
                               ' Path specified was', path)

        self.path = self.get_abs_path(path)
        self.contents = self.get_dir_contents()

    @staticmethod
    def get_abs_path(path):
        return os.path.realpath(path)

    def get_dir_contents(self):
        return os.listdir(self.path)

    def create_dir(self, path):
        os.makedirs(path)
        self.path = self.get_abs_path(path)

    def get_contents_with_full_path(self):
        return ['/'.join([self.path, _file]) for _file in self.contents]

    def set_contents_with_full_path(self):
        self.contents = self.get_contents_with_full_path()

    @staticmethod
    def compare_file_suffices(_file, suffix, ignore_case):
        if ignore_case:
            if _file.suffix.lower() == suffix.lower():
                return True
        else:
            if _file.suffix == suffix:
                return True

    def get_files_with_suffix(self, suffix, ignore_case=False):
        """
        This function returns a list of the contents of the directory whose
        instance we are in.

        Arguments:
            suffix: This is the file ending to look for. Directories which
                    also happen to have this ending are filtered out. The
                    suffix _DOES NOT_ include the dot. For example 'py' instead
                    of '.py'.
            ignore_case: Should case be ignored during the lookup? Default
                         is no. Change at your own peril.
        """
        files_with_suffix = []
        # ALWAYS send the ABSOLUTE paths to the File class.
        # Also filter out the directories.
        for file_path in self.get_contents_with_full_path():
            if not os.path.isdir(file_path):
                _file = File(file_path)
                if self.compare_file_suffices(_file, suffix, ignore_case):
                    files_with_suffix.append(_file.path)

        if len(files_with_suffix):
            return files_with_suffix


class File(object):
    """
    Models a file along with a few of its properties.
    Those properties are:
        path: string, The path of the file.
        suffix: string, The file ending.
    """

    def __init__(self, path):
        """
        Returns a File object whose path is *path*, *suffix* is the
        file ending. If it passes the sanity checks that is.

        Paths are always absolute to the filesystem root for consistency.
        We are assuming that all the paths that make it to this point are
        absolute ones since all of them are passed through the Directory class.
        """
        if not isinstance(path, str):
            raise TypeError('Path should be a string.'
                            ' Instead, path has a type of', type(path),
                            'and a value of', path)

        self.path = path
        self.suffix = self.get_file_suffix()

    def get_file_suffix(self):
        return os.path.splitext(self.path)[1][1:]


class Executable(File):
    """
    Models an EXECUTABLE file. Also inherits from File.
    Only property is:
        path: string, The path of the executable file.
    """

    def __init__(self, exec_name):
        super(Executable, self).__init__(exec_name)
        self.path = self.locate_executable()

    def locate_executable(self):
        """
        Use 'which' to check for the presence of the specified command.

        :param: None.
        :return: The output of which for success, otherwise None.
        """
        abs_path = None
        try:
            abs_path = subprocess.check_output(['which', self.path])
        except subprocess.CalledProcessError as e:
            print 'Could not locate program', self.path, 'Error was:', e

        if abs_path:
            return abs_path.rstrip()
        else:
            return None
