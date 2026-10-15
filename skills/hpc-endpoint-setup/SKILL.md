---
name: hpc-endpoint-setup
description: Use when the user asks to connect to Aurora, Perlmutter, or Frontier with hpc-bridge, install genesis_mission_hackathon on that system, or set up the Globus Compute endpoint that runs the hackathon tasks on compute nodes there, or start, check, or stop it. Covers Module 0 of this repo.
---

# Set up the hackathon endpoint on an HPC system with hpc-bridge

The goal is the state that Module 1 to 4 need:

- `~/genesis_mission_hackathon` on the system, installed with `uv sync`.
- The endpoint that hpc-bridge makes, `hpc-bridge-<facility>`, online. **By default, tasks run on compute nodes**: the endpoint submits a PBS job (Aurora) or a Slurm job (Perlmutter) for them, and the workers run in the repo `.venv`.
- Its UUID in `settings.env` on this computer, and `remote_function_call.py` returning `Hello World from <compute node>`.

A login-node endpoint (`gm_endpoint`) is the fallback. Use it only if the user asks for the login node, or has no allocation (section 7).

Follow the `hpc-bridge:driving-hpc` guidance for the tools. This skill adds what that guidance does not know about this repo and these systems.

| System | `facility` | `ssh_host` | `settings.env` variables | Notes |
|---|---|---|---|---|
| Aurora | `aurora` | `aurora.alcf.anl.gov` | `AURORA_ENDPOINT_ID`, `AURORA_ACCOUNT`, `AURORA_QUEUE` | Compute nodes tested (`x4…`). MobilePASS+ MFA. |
| Perlmutter | `perlmutter` | `perlmutter.nersc.gov` | `PERLMUTTER_ENDPOINT_ID`, `PERLMUTTER_ACCOUNT`, `PERLMUTTER_RESERVATION` | Compute nodes tested (`nid…`). |
| Frontier | `frontier` | `frontier.olcf.ornl.gov` | `FRONTIER_ENDPOINT_ID` | Not tested yet. |

## Rules

- Run every setup command with `run_shell(shape="login")`. Do not call `ensure_endpoint_up`: the compute nodes come from `user_endpoint_config` in the task (section 5), not from hpc-bridge's own compute block.
- Compute-node tasks use the user's allocation. Read the account from `settings.env` (`<SYSTEM>_ACCOUNT`); if it is empty, ask the user for it. Before the first compute-node submit, tell the user that it submits one 10 min `debug` job on their account, and get their OK.
- The user does the steps labelled **(user)** in their own terminal. Give them the exact command.
- Never ask for, type, or show a password or a PIN. Do not show the contents of `settings.env`.
- The plugin's credential guard blocks any command that contains `password=`, `token=`, `secret=`, or `api_key=` (also with `:`). Do not write such strings, not even in a `grep`.

## 1. Before you connect (user)

hpc-bridge reads the SSH user name only from `~/.ssh/config`. On a computer without an entry for the system, every SSH goes out as the local user name and fails.

Before the first `connect_facility` for Aurora or Perlmutter, find out if the user name is known. Do not print the whole file; it can hold other secrets:

```bash
ssh -G <ssh_host> 2>/dev/null | grep '^user '
```

If the result is the local user name (`whoami`), the user name is not known. First look for a short alias for the system, such as `Host aurora` or `Host perlmutter` (`ssh -G aurora 2>/dev/null | grep -E '^(user|hostname) '`). If the alias has a login node of that system as `hostname` (for example `perlmutter-p1.nersc.gov`) and a user name, use the alias as `ssh_host` and do not ask. But if `~/.hpc-bridge/endpoints.json` already has a key that starts with the full `ssh_host` from the table, keep the full name: hpc-bridge finds an endpoint by the `ssh_host` it was made with, so a different name makes a second endpoint. Then ask the user for their user name on that system (for example with `AskUserQuestion`). Do not guess it from the local user name or the email address. Give them this one command to run, with the `ssh_host` from the table (do not edit the file yourself). `~/.ssh` may not exist yet, so keep the `mkdir`:

```bash
mkdir -p ~/.ssh && chmod 700 ~/.ssh && printf 'Host <ssh_host>\n  User <their-user-name>\n' >> ~/.ssh/config && chmod 600 ~/.ssh/config
```

Check the result again with `ssh -G <ssh_host> | grep '^user '`: it must show their user name.

If `connect_facility` fails with `UNKNOWN HOST KEY`, the user runs `ssh aurora.alcf.anl.gov` once, accepts the fingerprint, logs in, and exits. Then call `connect_facility` again.

**Interactive SSH never works through the `!` prefix in Claude Code**: `!` has no terminal, so SSH cannot ask for the fingerprint or the passcode. Every `ssh` command in this skill is for the user's own terminal window.

## 2. Connect

```
connect_facility(facility="aurora", ssh_host="aurora.alcf.anl.gov")
```

| Result | Do this |
|---|---|
| `needs_login` | A Globus login. Give the user `login_url`; they paste the code back; call `complete_login(code)`. This one login also serves `globus_compute_sdk` on this computer. |
| `needs_preauth` | **On ALCF, skip `complete_preauth`** even if `preauth_code_ok` is `true`: Aurora labels its passcode prompt `Password:`, so `complete_preauth` refuses it and the passcode is wasted. **(user)** Give the user the `preauth_command` exactly as returned (no `user@`; the config supplies it). They run it in their own terminal window, not with `!`, and type the MobilePASS+ passcode at `Password:`. When they say it is done, call `connect_facility` again. |
| `proposed_facility_details` | Show the proposal and confirm it with the user. For Aurora, `interface` must be `hsn0`, `scheduler` `pbs`, `partition` `debug`. Set `scheduler_options` to `#PBS -l filesystems=home:flare`; Aurora rejects jobs without it. Then call `connect_facility(..., details=<confirmed>)`. |
| `provisioning` | Call again after a short wait. "allocating nodes" here means the free login-node worker; no job is queued. |
| `needs_account` | **Ready.** Do not look for an allocation with hpc-bridge; the account goes in `user_endpoint_config` (section 5). Continue with step 3. |

## 3. Install the repo

The `run_shell` environment has hpc-bridge's own virtualenv active and carries the variables `GLOBUS_COMPUTE_ENDPOINT_DIR`, `GLOBUS_COMPUTE_ENDPOINT_NAME`, and `GLOBUS_COMPUTE_LOG_PATH` from hpc-bridge's endpoint. Leave them in place and `globus-compute-endpoint start gm_endpoint` fails with exit code 73 ("Another instance of this endpoint is running"), because it acts on hpc-bridge's endpoint instead of `gm_endpoint`. **Start every command in steps 3 and 4 with:**

```bash
deactivate 2>/dev/null; unset VIRTUAL_ENV GLOBUS_COMPUTE_ENDPOINT_DIR GLOBUS_COMPUTE_ENDPOINT_NAME GLOBUS_COMPUTE_LOG_PATH;
```

Then:

```bash
cd ~ && { [ -d genesis_mission_hackathon ] || git clone -q https://github.com/academy-agents/genesis_mission_hackathon.git; }
cd ~/genesis_mission_hackathon && git pull -q --ff-only && uv sync -q
uv run python -c "import intermediate.custom_agents, rdkit, academy; print('imports ok')"
uv run globus-compute-endpoint version
```

If `git pull --ff-only` fails, the user has local changes on the system. Stop and tell them.

## 4. Find the compute endpoint

hpc-bridge already made the endpoint in step 2. Its name is `hpc-bridge-<facility>` (for example `hpc-bridge-aurora`). Get its UUID from `~/.hpc-bridge/endpoints.json` on this computer (the key `<ssh_host>::hpc-bridge-<facility>`), or from `uv run globus-compute-endpoint list` on the system (with the step 3 prefix). The UUID is stable across restarts.

Its UEP template branches on the **boolean** `compute`. With no `user_endpoint_config` it defaults to `compute: true` and an empty account, so a bare submit fails with `qsub: Account_Name is required`. Every task must send one of the configs in section 5.

**Make the compute workers use the repo `.venv`.** hpc-bridge's template sets the default `worker_init` to its own `~/.hpc-bridge/gce-venv`, which has only `globus-compute-endpoint` and none of the repo packages. Change the default to the repo `.venv`. Do this after every new provision, because hpc-bridge writes its own template again when it makes the endpoint:

```bash
cd ~/.globus_compute/hpc-bridge-<facility> && cp user_config_template.yaml.j2 user_config_template.yaml.j2.orig && python3 - <<'EOF'
import re
p = "user_config_template.yaml.j2"
s = open(p).read()
new = '    worker_init: {{ worker_init | default("source $HOME/genesis_mission_hackathon/.venv/bin/activate") }}'
s, n = re.subn(r"^    worker_init: \{\{ worker_init \| default\(.*\) \}\}$", new, s, flags=re.M)
assert n == 1, n
new = "  max_workers_per_node: {{ max_workers_per_node | default(12) }}"
s, n = re.subn(r"^  max_workers_per_node: \{\{ max_workers_per_node \| default\(.*\) \}\}$", new, s, flags=re.M)
assert n == 1, n
open(p, "w").write(s)
EOF
grep -n -E 'worker_init|max_workers_per_node' user_config_template.yaml.j2
```

The `grep` must show the `genesis_mission_hackathon/.venv` default and `default(12)`. The login-node config (section 5) still sends `max_workers_per_node: 1`, which replaces the default. You do not need to restart the endpoint: the manager renders the template again for each new UEP. A `worker_init` that the task sends still replaces the default; Aurora tasks that need the internet send the proxy and the venv together (section 5).

## 5. Update `settings.env` and test (local)

Set the endpoint variable for the system to the hpc-bridge UUID. Comment out an older value instead of deleting it. Do not print the file:

```bash
sed -i.bak -e 's/^AURORA_ENDPOINT_ID=\(.*\)/# AURORA_ENDPOINT_ID=\1\nAURORA_ENDPOINT_ID=<uuid>/' settings.env && rm settings.env.bak
```

Check that `AURORA_ACCOUNT` and `AURORA_QUEUE`, or `PERLMUTTER_ACCOUNT` and `PERLMUTTER_RESERVATION`, are set without printing them (`os.environ.get(...)` is truthy).

**Compute-node config (the default).** `intermediate/00_endpoint_setup/remote_function_call.py` has the tested values; reuse them:

| Key | Aurora | Perlmutter |
|---|---|---|
| `compute` | `True` (a bool) | `True` |
| `account` | `AURORA_ACCOUNT` | `PERLMUTTER_ACCOUNT` |
| `partition` | `"debug"` (the PBS queue) | `"debug"` |
| `walltime` | `"00:10:00"` | `"00:10:00"` |
| `max_workers_per_node` | omit (template default 12) | omit (template default 12) |
| `scheduler_options` | `"#PBS -l filesystems=home:flare"` (required, or the job is held) | `"#SBATCH --constraint=gpu\n#SBATCH --reservation=<PERLMUTTER_RESERVATION>"`: put the value of `PERLMUTTER_RESERVATION` into the string in Python, because Slurm does not expand `$VAR` in `#SBATCH` lines |
| `worker_init` | `export http_proxy=http://proxy.alcf.anl.gov:3128 https_proxy=http://proxy.alcf.anl.gov:3128; source $HOME/genesis_mission_hackathon/.venv/bin/activate` | `source $HOME/genesis_mission_hackathon/.venv/bin/activate` |

Aurora compute nodes reach the internet (Globus, the Academy exchange, the MAG) only through the ALCF proxy. Do not quote strings yourself; the endpoint quotes them.

After the user's OK, run from the repository root: `uv run python intermediate/00_endpoint_setup/remote_function_call.py`. Run it in the background: the job waits in the queue first (Aurora took about 10 min). It must print `Hello World from x4…` (Aurora) or `nid…` (Perlmutter). While it waits, watch the job with `run_shell("qstat -u $USER", shape="login")` or `squeue -u $USER`.

**Login-node config (only for quick checks, no allocation).** Send all three keys; `compute: False` alone still renders a PBS/Slurm provider and fails:

```python
{"compute": False, "provider_type": "LocalProvider", "max_workers_per_node": 1}
```

In a `ShellFunction`, `{name}` is a format field. Write a shell `${var%x}` as `${{var%x}}`, or the task fails with `KeyError`.

Report to the user: the system, the endpoint name and UUID, the compute-node host name from the test, that `settings.env` was updated, and that the test used one short `debug` job on their account.

If the test fails, read the UEP log and the submit script on the system: `~/.globus_compute/uep.<endpoint-uuid>.*/endpoint.log` and `submit_scripts/`. A transient `ssl.SSLError: unknown error` at UEP start is harmless; the endpoint retries and connects.

## 6. Stop

Leave `hpc-bridge-<facility>` running; it costs nothing while idle (`min_blocks` is 0, so idle compute jobs end). Only `teardown_endpoint` if the user asks for that explicitly. A queued or running compute job is cancelled with `qdel <id>` / `scancel <id>` through `run_shell(shape="login")`.

## 7. Fallback: `gm_endpoint` on the login node

Use this only if the user asks for the login node or has no allocation. Use the step 3 prefix on every command.

1. Make sure the system is logged in to Globus: `uv run globus-compute-endpoint whoami`. If it is not, **(user)** the user runs the login over the SSH connection from step 2:
   ```bash
   ssh -o ControlPath=$HOME/.hpc-bridge/cm/%C aurora.alcf.anl.gov 'cd ~/genesis_mission_hackathon && uv run globus-compute-endpoint login'
   ```
2. Configure once: `[ -d ~/.globus_compute/gm_endpoint ] || uv run globus-compute-endpoint configure gm_endpoint`. The default template runs tasks on the login node.
3. Start it detached: `uv run globus-compute-endpoint start --detach gm_endpoint`. Do not use `setsid`, `nohup`, or `&`. Without `--detach`, `start` never returns. If it returns 73, the variables in step 3 were not unset.
4. Check: `uv run globus-compute-endpoint list` must show `gm_endpoint` as `Running`. Put its UUID in `<SYSTEM>_ENDPOINT_ID` and test with `remote_function_call.py`.
5. To stop it: `uv run globus-compute-endpoint stop gm_endpoint`.
