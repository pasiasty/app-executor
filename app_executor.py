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
        for p_name, p_object in self.child_processes.items():
            if p_object.is_alive():
                logging.info('Finishing {}'.format(p_name))
                p_object._finish_gracefully()

            p_object._analyze_core_dump()

    def run(self, alias, cmd):
        if alias in self.child_processes:
            raise Exception('Duplicating alias: {}'.format(alias))

        new_process = Process(alias, cmd, self.context_dir)
        new_process._run()

        self.child_processes[alias] = new_process

        return new_process

    def get_process(self, alias):
        if alias not in self.child_processes:
            raise Exception('Alias {} not found!'.format(alias))

        return self.child_processes[alias]
