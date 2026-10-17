# Scaling Multi-Agent Systems

This repository is setup to run on ALCF Aurora. If running on another machine, you will need to set the environment variables manually and use a different qsub command. 

## Before you start

1. Clone this repo.
2. (if you don't have uv) Install and setup uv
   ```bash
   $ curl -LsSf https://astral.sh/uv/install.sh | sh
   $ source .venv/bin/activate
   $ uv sync
   ```

3. Install tutorial dependencies 
   ```bash
   $ source .venv/bin/activate
   $ cd gm_hackathon_scaling_agents
   $ uv sync
   ```

4. Start an interactive compute node on Aurora (for another machine consult documentation on the appropriate submit command)
   ```bash
   $ qsub -I -q R8914313 -l select=1,walltime=01:00:00 -A GenesisHackathonOct26 -l filesystems=home:flare
   ```

5. Configure access to a model by creating an access token. E.g., via the Model Access Gateway (MAG), local inference service, or commercial provider. For MAG, refer to [MAG get started](https://amsc-docs-d762d2.gitlab.io/mag-get-started). 

5. Update `aurora_env_setup.sh` with your AMSC token. This script includes environment variables for running on an Aurora compute node. 
   
7. Activate uv environment on the compute node
   ```bash
   $ source .venv/bin/activate
   $ source aurora_env_setup.sh
   ```

Note: if you are not running on Aurora, you can manually set the environment variables. This example uses the MAG with the Google provider and gemini-4-argon.  
 
  ```bash
   $ export AMSC_TOKEN=<INSERT YOUR TOKEN>
   $ export ANTHROPIC_AUTH_TOKEN=$AMSC_TOKEN
   $ export ANTHROPIC_BASE_URL=https://mag.genesis.americansciencecloud.org
   $ export ANTHROPIC_CUSTOM_HEADERS="X-AmSC-MAG-Provider: google"
   $ export LLM_MODEL=gemini-4-argon
   ```

### Scaling Agents

Each script runs Wordle agents. The agents use the Claude Agent SDK, and Academy runs the agents and enables communication between agents. Wordle is a small model of an expensive simulation: each guess is one evaluation, and the feedback tells the agent how near it is to the answer.

| Script | Pattern | Agents |
|---|---|---|
| `1_independent.py` | **Independent.** Each agent plays alone. | 2 `WordleAgent` |
| `2_message_board.py` | **Peers.** The agents share what they learn on a blackboard. | 2 `WordleAgent` |
| `3_multi_strategy.py` | **Coordinator and sub-agents.** The sub-agents test strategies on a cheap simulator. Then the coordinator plays the real game one time with the best strategy. | 1 `CoordinatorAgent` and 3 `StrategyAgent` |
