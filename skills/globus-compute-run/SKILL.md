---
name: globus-compute-run
description: Use when the user asks to run Python code, a shell command, or an application on a remote system or HPC endpoint (Aurora, Perlmutter, Frontier, or the tutorial endpoint) with Globus Compute.
---

# Run code on remote endpoints with Globus Compute

Globus Compute runs a function on a remote endpoint and sends the result back.
Use a Python function for Python code.
Use a `ShellFunction` for shell commands and applications.

## 1. Select the endpoint

The endpoint IDs are in `settings.env` in the project root.

| System | Variable |
|---|---|
| Aurora | `AURORA_ENDPOINT_ID` |
| Perlmutter | `PERLMUTTER_ENDPOINT_ID` |
| Frontier | `FRONTIER_ENDPOINT_ID` |
| Tutorial (public) | `TUTORIAL_ENDPOINT_ID` |

If the user does not name a system, use the tutorial endpoint.
If the variable is empty, stop. Tell the user to set up an endpoint with `intermediate/00_endpoint_setup/README.md`.

## 2. Run a Python function

```python
import os

import dotenv
from globus_compute_sdk import Executor

dotenv.load_dotenv(dotenv.find_dotenv("settings.env", usecwd=True))
ENDPOINT_ID = os.environ["TUTORIAL_ENDPOINT_ID"]


def remote_task(n: int) -> dict:
    """Run on the remote endpoint. Put all imports inside the function."""
    import platform

    return {"host": platform.node(), "squares": [i * i for i in range(n)]}


with Executor(endpoint_id=ENDPOINT_ID) as ex:
    future = ex.submit(remote_task, 5)
    try:
        print(future.result(timeout=300))
    except TimeoutError:
        print("Task did not finish in 300 s")
```

The function must be self-contained:
- Put all imports inside the function.
- Do not use global variables. Send all data as arguments.
- Use arguments and return values that pickle, for example numbers, strings, lists, and dicts.

If the remote function raises an exception, `future.result()` raises the same exception here.

## 3. Run a shell command or an application

```python
import os

import dotenv
from globus_compute_sdk import Executor, ShellFunction

dotenv.load_dotenv(dotenv.find_dotenv("settings.env", usecwd=True))
ENDPOINT_ID = os.environ["TUTORIAL_ENDPOINT_ID"]

cmd = ShellFunction("echo {message} && pwd && python3 --version", walltime=60)

with Executor(endpoint_id=ENDPOINT_ID) as ex:
    future = ex.submit(cmd, message="hello")
    try:
        result = future.result(timeout=300)
    except TimeoutError:
        print("Task did not finish in 300 s")
    else:
        print("returncode:", result.returncode)
        print("stdout:", result.stdout)
        print("stderr:", result.stderr)
        print("cmd:", result.cmd)
```

- Put arguments in `{name}` fields in the command. Send their values as keyword arguments to `submit`.
- `walltime` is the time limit in seconds for the command.
- A failed command does not raise an exception. Examine `returncode`. A value that is not 0 is a failure.
- `stderr` can contain endpoint warnings when the command is successful. Use `returncode` to find failures.
- `stdout` and `stderr` contain only the last 1000 lines.

## 4. Rules

- The code runs on the remote system. Packages, files, and paths must exist on the remote system, not on this computer.
- Write each submit script to a temporary file. Run it from the repository with `uv run python <script>`.
- Always set a timeout on `future.result()`.
- Do not write endpoint IDs in the script. Read them from `settings.env`.
- Aurora, Perlmutter, and Frontier are shared systems. Before you submit to them, show the user the function or the command.

## 5. Report the result

Tell the user:
- The endpoint name.
- The result, or `stdout` and `returncode`.
- The error, if the task failed.
