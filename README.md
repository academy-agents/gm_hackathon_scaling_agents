# Advanced modules

In the intermediate modules, an agent used a tool on an HPC system, ran in a LangGraph loop, and then ran as many copies on Aurora with Academy.

In the advanced modules, you build these parts yourself:

| Module | Pattern | What you learn |
|---|---|---|
| [1. Tool calling](1_tool_calling/) | An LLM selects which HPC function to run | How to make a Globus Compute function into an LLM tool |
| [2. Agent tool calling](2_agent_tool_calling/) | A coding agent calls HPC tools | How an agent can scale tool calls using Globus Compute |
| [3. Scaling agents](3_scaling_agents/) | Many LLM agents work on one problem | Three ways to organize agents: independent, peers, and coordinator with sub-agents |

## Before you start

1. Install this repo. Refer to the [top-level README](../README.md).
2. For Module 1, you need a Globus Compute endpoint. Refer to [intermediate Module 0](../intermediate/00_endpoint_setup/README.md) or use an existing Globus Compute endpoint (e.g., on ALCF Polaris).
3. For Module 2, install Docker or setup a Pi agent locally.
4. Configure access to a model. E.g., via the Model Access Gateway (MAG), local inference service, or commercial provider.

For MAG, refer to [MAG get started](https://amsc-docs-d762d2.gitlab.io/mag-get-started). Then put the token in your shell:

   ```bash
   export AMSC_TOKEN=<your MAG key>
   ```

For the ANL Inference service. You can obtain a token as follows:

   ```bash
   uvx --from "alcf-ai==0.10.0" alcf-ai auth login
   ```

## 1. Tool calling

The decorator `gce_wrapper` sends each function call to Globus Compute and waits for the result. The LLM sees a usual Python function with a name, a docstring, and type hints. The LLM does not know that the function runs on an HPC system.

| File | What it does |
|---|---|
| `test_globus_compute.py` | Runs `hello_world` on the endpoint. Run this file first to test the endpoint. |
| `tool_calling_globus_compute.py` | Gives an LLM three tools: count primes, calculate molecular energy, and run an MD trajectory. The script asks one random question, and the LLM selects the tool to run. |


## 2. Agent tool calling

[Pi](https://pi.dev) combined with a [Globus Harness](https://github.com/GusEllerm/pi-lab-profile) profile runs in a Docker container. The agent uses its built-in tools (read, edit, bash) and the [hpc-bridge](https://github.com/globus-labs/hpc-bridge) MCP tools to do work on an HPC system.


## 3. Scaling agents

Each script runs Wordle agents. The agents use the Claude Agent SDK, and Academy runs them. Wordle is a small model of an expensive simulation: each guess is one evaluation, and the feedback tells the agent how near it is to the answer.

| Script | Pattern | Agents |
|---|---|---|
| `1_independent.py` | **Independent.** Each agent plays alone. | 2 `WordleAgent` |
| `2_message_board.py` | **Peers.** The agents share what they learn on a blackboard. | 2 `WordleAgent` |
| `3_multi_strategy.py` | **Coordinator and sub-agents.** The sub-agents test strategies on a cheap simulator. Then the coordinator plays the real game one time with the best strategy. | 1 `CoordinatorAgent` and 3 `StrategyAgent` |
