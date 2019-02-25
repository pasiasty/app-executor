import pytest
import app_executor


@pytest.fixture()
def executor(tmpdir):
    with app_executor.AppExecutor(tmpdir) as app_exec:
        yield app_exec
