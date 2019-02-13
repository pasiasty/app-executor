def test_simple_run(executor):
    executor.run('whoami', 'Whoami')
    executor.wait('Whoami', 10)
    assert 'mpasek' == executor.get_logfile('Whoami').strip()
