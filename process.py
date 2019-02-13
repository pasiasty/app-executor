import os
import shutil
import logging
import re
import subprocess


class Process:
    @staticmethod
    def _parse_cmd(cmd):
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

    def __init__(self, name, cmd, parent_context_dir):
        self.name = name
        self.context_dir = os.path.join(parent_context_dir, name)
        self.exec_name, self.args = Process._parse_cmd(cmd)

        if os.path.isdir(self.context_dir):
            shutil.rmtree(self.context_dir)
        os.makedirs(self.context_dir)

        self.popen = None
        self.outfd = None

    def is_alive(self):
        if self.popen is None:
            raise Exception('Checking for being alive on not-launched process')

        return self.popen.poll() is None

    def terminate(self):
        self.popen.terminate()

    def kill(self):
        self.popen.kill()

    def get_rc(self):
        if self.is_alive():
            raise Exception('Process {}: Getting rc before process completion!'.format(self.name))

        gdb_log = open(self._get_gdb_log_path(), 'r').read()

        if re.match(r'\[Inferior [1-9][0-9]* \(process [1-9][0-9]*\) exited normally\]', gdb_log):
            return 0
        m = re.search(r'\[Inferior [1-9][0-9]* \(process [1-9][0-9]*\) exited with code ([0-9]+)\]', gdb_log)
        return int(m.group(1))

    def wait(self, timeout=5, silent=False):
        try:
            self.popen.wait(timeout)
        except subprocess.TimeoutExpired:
            if not silent:
                logging.error('Process {}: timeout reached'.format(self.name))
            return False

        return True

    def get_logfile(self):
        return open(self._get_log_path(), 'r').read().strip()

    def _run(self):
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

    def _get_log_path(self):
        return os.path.join(self.context_dir, 'log.txt')

    def _get_gdb_log_path(self):
        return os.path.join(self.context_dir, 'gdb.txt')

    def _get_core_dump_path(self):
        return os.path.join(self.context_dir, 'core_dump.bin')

    def _get_stacktrace_path(self):
        return os.path.join(self.context_dir, 'stacktrace.txt')

    def _analyze_core_dump(self):
        if os.path.isfile(self._get_core_dump_path()):
            os.system('gdb {exec_path} {core_dump_path} -batch -ex "where" '
                      '-ex "thread apply all bt" > {stacktrace_path} 2>&1'
                      .format(exec_path=self.exec_name, core_dump_path=self._get_core_dump_path(),
                              stacktrace_path=self._get_stacktrace_path()))

    def _finish_gracefully(self, timeout=1):
        if self.wait(timeout, silent=True):
            return
        self.outfd.flush()
        if self.popen:
            if self.is_alive():
                self.terminate()
            if self.is_alive():
                self.kill()
