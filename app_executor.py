import logging
import os
from process import Process


class AppExecutor:

    def __init__(self, context_dir):
        if not os.path.isdir(context_dir):
            os.makedirs(context_dir)

        self.context_dir = context_dir
        self.child_processes = {}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.kill_all_processes()

    def run(self, cmd, alias):
        if alias in self.child_processes:
            raise Exception('Duplicating alias: '.format(alias))

        new_process = Process(alias, cmd, self.context_dir)
        new_process.run()

        self.child_processes[alias] = new_process

    def kill_all_processes(self):
        for p_name, p_object in self.child_processes.items():
            if p_object.is_alive():
                logging.info('Finishing {}'.format(p_name))
                p_object.finish_gracefully()

    def _get_process_object(self, alias):
        if alias not in self.child_processes:
            raise Exception('Alias {} not found!'.format(alias))

        return self.child_processes[alias]

    def wait(self, alias, timeout=0):
        self._get_process_object(alias).wait(timeout)

    def terminate(self, alias):
        self._get_process_object(alias).terminate()

    def kill(self, alias):
        self._get_process_object(alias).kill()

    def get_rc(self, alias):
        self._get_process_object(alias).get_rc()

    def get_logfile(self, alias):
        return open(self._get_process_object(alias).get_log_path(), 'r').read()
