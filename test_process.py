from process import Process
import logging

logging.basicConfig(level=logging.DEBUG)

p = Process('MySleep', 'whoami', '.')
p.run()
p.finish_gracefully()
