import pytest
import app_executor


@pytest.yield_fixture()
def executor(tmpdir):
    """
    return app_executor.AppExecutor object that will allow to run arbitrary number of
    processes. In teardown it will stop them and perform dump analysis. All results will be
    put into temporary directory.
    """
    with app_executor.AppExecutor(tmpdir) as app_exec:
        yield app_exec
