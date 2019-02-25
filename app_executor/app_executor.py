import logging
import os
import re
from app_executor.process import Process


class AppExecutor:
    """
    Class used managing running arbitrary number of processes. It makes sure that
    on it's exit step all launched processes will be properly stopped and their dumps
    analyzed (if collected).
    """

    def __init__(self, context_dir):
        """
        :param context_dir: directory in which all processes directories will be located
        """

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
        """
        Used for running a process

        :param cmd: command to be executed
        :param alias: alias to be assigned to just spawned process (if None 'process_XXX'
        where XXX is a number will be assigned)
        :return: returns object of just spawned process
        """

        if alias:
            if alias in self.child_processes:
                raise Exception('Duplicating alias: {}'.format(alias))
        else:
            alias = self._get_next_unique_alias()

        new_process = Process(alias, cmd, self.context_dir)
        new_process.run()

        self.child_processes[alias] = new_process

        return new_process

    def _get_next_unique_alias(self):
        num_of_auto_aliases = sum(1 for el in self.child_processes.keys() if re.match(r'process_[1-9][0-9]*', el))
        return 'process_{}'.format(num_of_auto_aliases + 1)

    def get_process(self, alias):
        """
        Lets to get process object that has been previously spawned by AppExecutor.

        :param alias: alias of the process that should be looked up
        :return: object of the found process
        """

        if alias not in self.child_processes:
            raise Exception('Alias {} not found!'.format(alias))

        return self.child_processes[alias]
