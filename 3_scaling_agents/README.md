# Scaling Agents

In this module, you will use Academy to deploy a set of agents and experiment with different communication patterns. 

The examples are configured to run locally and use an in-memory exchange; however, this can be extended to use remote computing resources and a cloud messaging exchange for federated deployments. 

You will need to set environment variables to use Claude agents

```bash
export ANTHROPIC_AUTH_TOKEN=$AMSC_TOKEN
export ANTHROPIC_BASE_URL=https://mag.genesis.americansciencecloud.org
```

Each script runs Wordle agents. The agents use the Claude Agent SDK, and Academy runs them. Wordle is a small model of an expensive simulation: each guess is one evaluation, and the feedback tells the agent how near it is to the answer.

| Script | Pattern | Agents |
|---|---|---|
| `1_independent.py` | **Independent.** Each agent plays alone. | 2 `WordleAgent` |
| `2_message_board.py` | **Peers.** The agents share what they learn on a blackboard. | 2 `WordleAgent` |
| `3_multi_strategy.py` | **Coordinator and sub-agents.** The sub-agents test strategies on a cheap simulator. Then the coordinator plays the real game one time with the best strategy. | 1 `CoordinatorAgent` and 3 `StrategyAgent` |

At the end, each script shows the answer from each agent and the true target word.

All agents run in one process on your computer. Each agent is a `MonitoredAgent`: it sends its logs and status through the Academy cloud exchange (`HttpExchangeFactory`) to your `UserAgent` on the [dashboard](https://dashboard.academy-agents.org). Before you run a script, start your `UserAgent` and set `USER_AGENT_ID` in `settings.env`, as in intermediate [Module 4](../../intermediate/04_dashboard/README.md). To run agents on an HPC system, add a Globus Compute executor, as in intermediate Module 3.
