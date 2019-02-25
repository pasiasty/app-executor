import app_executor
import getpass


def test_parse_cmd():
    assert ('sleep', '1') == app_executor.Process.parse_cmd('sleep 1')
    assert ('whoami', '') == app_executor.Process.parse_cmd('whoami')
    assert ('"/my\'nice path\'/with chars"', ' 1 2 \'24\'') == app_executor.Process.parse_cmd(
        '"/my\'nice path\'/with chars" 1 2 \'24\'')
    assert ('\'/my"nice path"/with chars\'', ' 1 2 "24"') == app_executor.Process.parse_cmd(
        '\'/my"nice path"/with chars\' 1 2 "24"')


def test_simple_run(tmpdir):
    process_obj = app_executor.Process('Whoami', 'whoami', tmpdir)
    process_obj.run()
    process_obj.wait(10)
    assert getpass.getuser() == process_obj.get_logfile()


def test_always_failing_command(tmpdir):
    with app_executor.Process('MyFail', 'false', tmpdir) as my_fail_process:
        my_fail_process.wait()
        assert 1 == my_fail_process.get_rc()


def test_wait(tmpdir):
    process_obj = app_executor.Process('Sleep1', 'sleep 1', tmpdir)
    process_obj.run()
    assert process_obj.wait(2)
    process_obj = app_executor.Process('Sleep5', 'sleep 5', tmpdir)
    process_obj.run()
    assert not process_obj.wait(1, silent=True)

