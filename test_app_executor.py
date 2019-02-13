from app_executor import AppExecutor
import logging

logging.basicConfig(level=logging.DEBUG)

with AppExecutor('executions') as executor:
    executor.run('whoami', 'Whoami')
    executor.run('sleep 5', 'Sleep5')
    executor.run('sleep 1', 'Sleep1')
    executor.run('python3 explode.py', 'Explode')
