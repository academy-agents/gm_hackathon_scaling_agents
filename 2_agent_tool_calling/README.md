# Module 2: A coding agent that calls HPC tools

In [Module 1](../1_tool_calling/), you wrote the agent loop with LangChain and gave the LLM three Python functions as tools.
Here, you use a coding agent that has the loop and the tools already. The agent is [Pi](https://pi.dev) with the [Globus Harness](https://github.com/GusEllerm/pi-lab-profile) profile, and it runs in a Docker container (you can also set it up locally if you prefer by following the steps in the Dockerfile). The agent has two types of tools:

- **Built-in tools:** read, write, edit, bash, grep, find, and ls. They operate on the files in the container.
- **MCP tools from [hpc-bridge](https://github.com/globus-labs/hpc-bridge):** connect to an HPC facility, start a compute block, run commands on it, and stop it.

You do not need to write code. You can simply give the agent a task, and the agent selects the tools. It will use Globus Compute to access remote HPC resources. Here the agent will write Python code and run it interactively on provisioned compute resources. 


## 1. Build and start

Install Docker. On macOS and Windows, use Docker Desktop. Then, from this directory:

```bash
docker build -t gm-agent .
docker run -it --name gm-agent gm-agent
```

## 2. Log in to a model

In Pi, type `/login`. Select a provider, for example Anthropic, and paste your API key. Then type `/model` and select a model.

To use the ALCF inference service, you need an ALCF account. In a second terminal, log in:

```bash
docker exec -it gm-agent uvx --from "alcf-ai==0.10.0" alcf-ai auth login
```

Then type `/model` in Pi and select an `alcf-…` model.

## 3. Give the agent a task

Type these in Pi:

| Input | Result |
|---|---|
| `/mcp` | Shows the `hpc` server and its tools. |
| `What HPC facilities can I use?` | The agent calls hpc-bridge and shows the facilities. |
| `Connect to Polaris using the XXX allocation and the Debug queue.` | The agent connects to Polaris, starts a batch job, and deploys a interactive pilot job model for subsequent tool use.  |
| `Use  Polaris to execute a monte carlo simulation to compute Pi.` | The agent uses the allocated resources to run a series of tool calls.  |


If the system needs a password or a one-time passcode, the agent gives you an `ssh` command. Run the command inside the container, in a second terminal:

```bash
docker exec -it gm-agent <the ssh command from the agent>
```

> **Note:** Do not run the `ssh` command on your computer. hpc-bridge uses the SSH connection that you open in the container.

A compute block uses your allocation. The agent starts a compute block only after you confirm a dialog. When you are done, tell the agent to stop the endpoint. To see the facility, the block, and the node-hours, type `/hpc`.

## Start again later

When you exit Pi, the container stops. Your login and settings stay in the container. To start Pi again:

```bash
docker start -ai gm-agent
```

After you rebuild the image, remove the old container, then do `docker run` again:

```bash
docker rm gm-agent
```

**Challenge:** Tell the agent to do the [intermediate Module 1](../../intermediate/01_claude_code/README.md) task: calculate QED with RDKit on Aurora for aspirin and five similar molecules. Compare the result with the Claude Code result.
