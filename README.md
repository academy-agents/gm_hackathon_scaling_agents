# Scaling Multi-Agent Systems

## Before you start

1. Install this repo.
2. Setup uv and dependencies
  ```bash
   $ RUN curl -LsSf https://astral.sh/uv/install.sh | sh
   $ source ~/.venv/bin/activate
   $ uv sync
   ```

3. Start an interactive compute node
   ```bash
   $ qsub -I -q R8914313 -l select=1,walltime=01:00:00 -A GenesisHackathonOct26 -l filesystems=home:flare
   ```

4. Configure access to a model. E.g., via the Model Access Gateway (MAG), local inference service, or commercial provider.

For MAG, refer to [MAG get started](https://amsc-docs-d762d2.gitlab.io/mag-get-started). Then put the token in your shell:

   ```bash
   export AMSC_TOKEN=<your MAG key>
   ```

5. Update `aurora_env_setup` with your AMSC token
6. Activate uv environment on the compute node
    ```bash
   $ source ~/.venv/bin/activate
   ```
8. Run the code in scaling_agents

### Scaling Agents

Each script runs Wordle agents. The agents use the Claude Agent SDK, and Academy runs them. Wordle is a small model of an expensive simulation: each guess is one evaluation, and the feedback tells the agent how near it is to the answer.

| Script | Pattern | Agents |
|---|---|---|
| `1_independent.py` | **Independent.** Each agent plays alone. | 2 `WordleAgent` |
| `2_message_board.py` | **Peers.** The agents share what they learn on a blackboard. | 2 `WordleAgent` |
| `3_multi_strategy.py` | **Coordinator and sub-agents.** The sub-agents test strategies on a cheap simulator. Then the coordinator plays the real game one time with the best strategy. | 1 `CoordinatorAgent` and 3 `StrategyAgent` |
