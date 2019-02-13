import os
import shutil
import signal
import logging
import time
import re


class Process:
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

    def __init__(self, name, cmd, parent_context_dir):
        self.name = name
        self.context_dir = os.path.join(parent_context_dir, name)
        self.exec_name, self.args = Process.parse_cmd(cmd)
        self.pid = None

        if os.path.isdir(self.context_dir):
            shutil.rmtree(self.context_dir)
        os.makedirs(self.context_dir)

        self.outfd = None

    def run(self):
        self.pid = os.fork()
        self.outfd = open(self.get_log_path(), 'w')

        if self.pid < 0:
            raise Exception('Process {}: fork failed!'.format(self.name))
        elif self.pid == 0:
            import sys
            with open('/dev/null', 'r') as stdin:

                os.dup2(stdin.fileno(), sys.stdin.fileno())
                os.dup2(self.outfd.fileno(), sys.stdout.fileno())
                os.dup2(self.outfd.fileno(), sys.stderr.fileno())

                gdb_cmd = 'gdb -batch-silent -ex "set pagination off" -ex "set logging file {gdb_log_path}" ' \
                          '-ex "set logging on" -ex "run {args}" ' \
                          '-ex "generate-core-file {dump_path}" {exec_name}' \
                    .format(exec_name=self.exec_name,
                            args=self.args,
                            gdb_log_path=self._get_gdb_log_path(),
                            dump_path=self._get_core_dump_path())

                with open(self._get_gdb_log_path(), 'w') as gdb_log:
                    gdb_log.write(gdb_cmd + '\n\n')

                os.system(gdb_cmd)
                exit(0)
        else:
            logging.info('Process {} PID: {} cmd: {}'.format(
                self.name, self.pid, ' '.join([self.exec_name, self.args])))

    def get_log_path(self):
        return os.path.join(self.context_dir, 'log.txt')

    def _get_gdb_log_path(self):
        return os.path.join(self.context_dir, 'gdb.txt')

    def _get_core_dump_path(self):
        return os.path.join(self.context_dir, 'core_dump.bin')

    def _get_stacktrace_path(self):
        return os.path.join(self.context_dir, 'stacktrace.txt')

    def is_alive(self):
        if self.pid is None:
            raise Exception('Process {} was never ran'.format(self.name))

        try:
            os.kill(self.pid, 0)
            os.waitpid(self.pid, os.WNOHANG)
            os.kill(self.pid, 0)
        except OSError:
            return False
        return True

    def terminate(self):
        os.kill(self.pid, signal.SIGTERM)

    def kill(self):
        os.kill(self.pid, signal.SIGKILL)

    def get_rc(self):
        if self.is_alive():
            raise Exception('Process {}: Getting rc before process completion!'.format(self.name))

        gdb_log = open(self._get_gdb_log_path(), 'r').read()

        if re.match(r'\[Inferior [1-9][0-9]* \(process [1-9][0-9]*\) exited normally\]', gdb_log):
            return 0
        m = re.search(r'\[Inferior [1-9][0-9]* \(process [1-9][0-9]*\) exited with code ([0-9]+)\]', gdb_log)
        return int(m.group(1))

    def wait(self, timeout=5, silent=False):
        time_elapsed = 0

        while self.is_alive() and (timeout == 0 or time_elapsed < timeout):
            time_elapsed += 0.1
            time.sleep(0.1)

        if self.is_alive():
            if not silent:
                logging.error('Process {}: timeout reached for PID {}'.format(self.name, self.pid))
            return False

        return True

    def analyze_core_dump(self):
        if os.path.isfile(self._get_core_dump_path()):
            os.system('gdb {exec_path} {core_dump_path} -batch -ex "where" '
                      '-ex "thread apply all bt" > {stacktrace_path} 2>&1'
                      .format(exec_path=self.exec_name, core_dump_path=self._get_core_dump_path(),
                              stacktrace_path=self._get_stacktrace_path()))

    def finish_gracefully(self, timeout=1):
        if self.wait(timeout, silent=True):
            return
        self.outfd.flush()
        if self.pid:
            if self.is_alive():
                self.terminate()
            if self.is_alive():
                self.kill()
        os.waitpid(self.pid, 0)
