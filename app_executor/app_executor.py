import logging
import os
import re
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
                p_object.stop()

            p_object.analyze_core_dump()

    def run(self, cmd, alias=None):
        if alias:
            if alias in self.child_processes:
                raise Exception('Duplicating alias: {}'.format(alias))
        else:
            alias = self.get_next_unique_alias()

        new_process = Process(alias, cmd, self.context_dir)
        new_process.run()

        self.child_processes[alias] = new_process

        return new_process

    def get_next_unique_alias(self):
        num_of_auto_aliases = sum(1 for el in self.child_processes.keys() if re.match(r'process_[1-9][0-9]*', el))
        return 'process_{}'.format(num_of_auto_aliases + 1)

    def get_process(self, alias):
        if alias not in self.child_processes:
            raise Exception('Alias {} not found!'.format(alias))

        return self.child_processes[alias]
