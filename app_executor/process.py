import os
import shutil
import logging
import re
import subprocess


class Process:
    """
    Class used for managing invoking command. It lets to interact with spawned process,
    i.e.: waiting for it to finish, getting stdout and stderr of it and performing dump
    analysis.
    """

    @staticmethod
    def parse_cmd(cmd):
        m = re.search(r'^(".*?[^\\]")(.*)', cmd)

        if m is None:
            m = re.search(r'^(\'.*?[^\\]\')(.*)', cmd)
            if m is None:
                arr = cmd.split(' ')
                if len(arr) == 1:
                    return arr[0], ''
                else:
                    return arr[0], ' '.join(arr[1:])

        return m.group(1), m.group(2)

    def __enter__(self):
        self.run()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        self.analyze_core_dump()

    def __init__(self, name, cmd, parent_context_dir):
        """
        :param name: name of the process - processes directory will be named the same, this name will
        also occur in warning/error prints
        :param cmd: command to be executed
        :param parent_context_dir: directory in which process's directory should be created
        """
        self.name = name
        self.context_dir = os.path.join(parent_context_dir, name)
        self.exec_name, self.args = Process.parse_cmd(cmd)

        if os.path.isdir(self.context_dir):
            shutil.rmtree(self.context_dir)
        os.makedirs(self.context_dir)

        self.popen = None
        self.outfd = None

    def is_alive(self):
        """
        :return: True if process is still alive, False otherwise
        """
        if self.popen is None:
            raise Exception('Checking for being alive on not-launched process')

        return self.popen.poll() is None

    def terminate(self):
        """
        :return: attempts to terminate process
        """
        self.popen.terminate()

    def kill(self):
        """
        :return: attempts to kill process
        """
        self.popen.kill()

    def get_rc(self):
        """
        used for getting result code of executed process. It throws an exception if
        called prematurely.
        :return: result code of the command
        """

        if self.is_alive():
            raise Exception('Process {}: Getting rc before process completion!'.format(self.name))

        gdb_log = open(self._get_gdb_log_path(), 'r').read()

        if re.search(r'\[Inferior [1-9][0-9]* \(process [1-9][0-9]*\) exited normally\]', gdb_log):
            return 0
        m = re.search(r'\[Inferior [1-9][0-9]* \(process [1-9][0-9]*\) exited with code ([0-9]+)\]', gdb_log)
        return int(m.group(1))

    def wait(self, timeout=5, silent=False):
        """
        Waits for the process to finish.

        :param timeout: timeout for waiting
        :param silent: if set to True it will not produce error print on failure
        :return: True if process finished in given timeout, False otherwise
        """

        try:
            self.popen.wait(timeout)
        except subprocess.TimeoutExpired:
            if not silent:
                logging.error('Process {}: timeout reached'.format(self.name))
            return False

        return True

    def get_logfile(self):
        """
        :return: gets output (stdout and stderr combined) of executed process
        """
        return open(self._get_log_path(), 'r').read().strip()

    def run(self):
        """
        Runs the command
        """
        self.outfd = open(self._get_log_path(), 'w')

        gdb_cmd = 'gdb -batch-silent -ex "set pagination off" -ex "set logging file {gdb_log_path}" ' \
                  '-ex "set logging on" -ex "run {args}" ' \
                  '-ex "generate-core-file {dump_path}" {exec_name}' \
            .format(exec_name=self.exec_name,
                    args=self.args,
                    gdb_log_path=self._get_gdb_log_path(),
                    dump_path=self._get_core_dump_path())

        with open(self._get_gdb_log_path(), 'w') as gdb_log:
            gdb_log.write(gdb_cmd + '\n\n')

        self.popen = subprocess.Popen(gdb_cmd, shell=True, stdout=self.outfd, stderr=self.outfd)

    def analyze_core_dump(self):
        """
        Performs dump analysis if it has been collected.
        """
        if os.path.isfile(self._get_core_dump_path()):
            os.system('gdb {exec_path} {core_dump_path} -batch -ex "where" '
                      '-ex "thread apply all bt" > {stacktrace_path} 2>&1'
                      .format(exec_path=self.exec_name, core_dump_path=self._get_core_dump_path(),
                              stacktrace_path=self._get_stacktrace_path()))

    def stop(self, timeout=1):
        """
        Makes sure that processes is not running anymore after running this function.
        It first tries to wait for it, then terminate it and if that still fails - kill it.
        """

        if self.wait(timeout, silent=True):
            return
        self.outfd.flush()
        if self.popen:
            if self.is_alive():
                self.terminate()
            if self.is_alive():
                self.kill()

    def _get_log_path(self):
        return os.path.join(self.context_dir, 'log.txt')

    def _get_gdb_log_path(self):
        return os.path.join(self.context_dir, 'gdb.txt')

    def _get_core_dump_path(self):
        return os.path.join(self.context_dir, 'core_dump.bin')

    def _get_stacktrace_path(self):
        return os.path.join(self.context_dir, 'stacktrace.txt')
