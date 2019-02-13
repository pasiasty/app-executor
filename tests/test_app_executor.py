import pytest
import logging
import app_executor
import getpass


def test_simple_run(executor):
    executor.run('Whoami', 'whoami')
    executor.wait('Whoami', 10)
    assert getpass.getuser() == executor.get_logfile('Whoami').strip()


def test_alias_conflict(executor):
    executor.run('Sleep', 'sleep 1')

    with pytest.raises(Exception) as excinfo:
        executor.run('Sleep', 'sleep 5')

    assert 'Duplicating alias: Sleep' in str(excinfo.value)


def test_nonexisting_alias(executor):
    with pytest.raises(Exception) as excinfo:
        executor.wait('Sleep')

    assert 'Alias Sleep not found!' in str(excinfo.value)

    with pytest.raises(Exception) as excinfo:
        executor.terminate('Sleep')

    assert 'Alias Sleep not found!' in str(excinfo.value)

    with pytest.raises(Exception) as excinfo:
        executor.kill('Sleep')

    assert 'Alias Sleep not found!' in str(excinfo.value)

    with pytest.raises(Exception) as excinfo:
        executor.get_rc('Sleep')

    assert 'Alias Sleep not found!' in str(excinfo.value)

    with pytest.raises(Exception) as excinfo:
        executor.get_logfile('Sleep')

    assert 'Alias Sleep not found!' in str(excinfo.value)


def test_always_failing_command(executor):
    my_fail_process = executor.run('MyFail', 'false')
    my_fail_process.wait()
    assert 1 == my_fail_process.get_rc()


def test_wait(executor):
    process = executor.run('Sleep1', 'sleep 1')
    assert process.wait(2)
    process = executor.run('Sleep5', 'sleep 5')
    assert not process.wait(1, silent=True)


def test_killall(tmpdir, caplog):
    caplog.set_level(logging.INFO)

    with app_executor.AppExecutor(tmpdir) as app_exec:
        app_exec.run('Sleep1', 'sleep 50')
        app_exec.run('Sleep2', 'sleep 50')
        app_exec.run('Sleep3', 'sleep 50')

    assert ['Finishing Sleep1', 'Finishing Sleep2', 'Finishing Sleep3'] == [rec.message for rec in caplog.records]


