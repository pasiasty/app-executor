# app_executor

This program might be used for launching external executables from python script.
It can also collect `stdout` and `stderr` of them and store it into text file.
In case of any failure it can also provide some basic stacktrace collection.

Importing `app_executor` package gives an access to two essential classes:

* `app_executor.Process` - this class can be used for direct launching processes
* `app_executor.AppExecutor` - this class can be used for automatic managing of
launching multiple processes

## Example usage

### `app_executor.Process`

This code launches `whoami` and aliases it as `MyName` - all warning/error prints
will be having this alias for increasing readability. Then it runs the process
and waits up to 1 second for it to finish. In the end it prints result code and
actual output (stdout and stderr combined) of executed command.

In the exit step command will be stopped (firstly `app_executor.Process` will try
to terminate it and if that fails - kill it). And afterwards it will perform
core dump analysis (if core dump was collected during the execution).

All result files - logs from `gdb`, process itself, core dump and stacktrace will
be put into `/some/path/MyName` directory.

```python
import app_executor
with app_executor.Process(name='MyName',
                          cmd='whoami',
                          parent_context_dir='/some/path') as process:
    process.run()
    if not process.wait(timeout=1):
        raise Exception('Process hanged for too long!')

    print('Returncode was: {}'.format(process.get_rc()))
    print('Output of whoami: {}'.format(process.get_logfile()))
```

### `app_executor.AppExecutor`

This code works similar to former. Here execution path is passed once for all
processes launched later on. `app_executor.AppExecutor` can either assign
aliases by itself (`process_1`, `process_2`, etc.) or user can set them manually.

`run` function returns `app_executor.Process` object that can be used to interact
with the process later on (similarly as in former example).

In the exit step `app_executor.AppExecutor` will stop every child process and
perform dump analysis if core dump were collected. All result files will be stored
under the path `/some/path/$NAME_OF_THE_PROCESS`.

```python
import app_executor
with app_executor.AppExecutor('/some/path') as executor:
    p1 = executor.run('whoami')
    p2 = executor.run('sleep 1', 'MyCustomAlias')

    # ...
    # operations on p1 and p2 app_executor.Process objects
    # ...

```

### `executor` fixture

Together with installing `app_executor` package `executor` pytest fixture becomes
available. It creates `app_executor.AppExecutor` and passes `tmpdir` as work
directory to it. On fixture teardown all spawned processes are stopped.

```python

def test_some_executing(executor):
    p1 = executor.run('whoami')
    p2 = executor.run('sleep 1')

    # ...
    # operations on p1 and p2 app_executor.Process objects
    # ...

```