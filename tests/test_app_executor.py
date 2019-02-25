import pytest
import logging
import app_executor
import getpass


def test_simple_run(executor):
    executor.run('whoami', 'Whoami')
    process = executor.get_process('Whoami')
    process.wait(10)
    assert getpass.getuser() == process.get_logfile()


def test_alias_conflict(executor):
    executor.run('sleep 1', 'Sleep')

    with pytest.raises(Exception) as excinfo:
        executor.run('sleep 5', 'Sleep')

    assert 'Duplicating alias: Sleep' in str(excinfo.value)


def test_nonexisting_alias(executor):
    with pytest.raises(Exception) as excinfo:
        executor.get_process('Sleep')

    assert 'Alias Sleep not found!' in str(excinfo.value)


def test_always_failing_command(executor):
    my_fail_process = executor.run('false')
    my_fail_process.wait()
    assert 1 == my_fail_process.get_rc()


def test_wait(executor):
    process = executor.run('sleep 1')
    assert process.wait(2)
    process = executor.run('sleep 5')
    assert not process.wait(1, silent=True)


def test_killall(tmpdir, caplog):
    caplog.set_level(logging.INFO)

    with app_executor.AppExecutor(tmpdir) as app_exec:
        app_exec.run('sleep 50')
        app_exec.run('sleep 50')
        app_exec.run('sleep 50')

    assert ['Finishing process_1', 'Finishing process_2', 'Finishing process_3'] == [rec.message for rec in
                                                                                     caplog.records]


def test_auto_aliases(executor):
    p1 = executor.run('whoami')
    p2 = executor.run('whoami', 'Whoami')
    p3 = executor.run('whoami')
    p4 = executor.run('whoami')

    assert 'process_1' == p1.name
    assert 'Whoami' == p2.name
    assert 'process_2' == p3.name
    assert 'process_3' == p4.name
