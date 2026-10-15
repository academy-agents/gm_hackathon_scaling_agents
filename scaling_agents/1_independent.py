from __future__ import annotations

import asyncio
import logging
import os
from typing import Any
from uuid import UUID

import dotenv
from academy.agent import action
from academy.exchange.cloud import HttpExchangeFactory
from academy.handle import Handle
from academy.identifier import AgentId
from academy.logging.recommended import recommended_logging
from academy.manager import Manager
from academy_dashboard import MonitoredAgent, UserAgent
from claude_agent_sdk import (
    ClaudeAgentOptions,
    ResultMessage,
    create_sdk_mcp_server,
    query,
    tool,
)
from wordle import WordleGame

logger = logging.getLogger(__name__)


class WordleAgent(MonitoredAgent):
    """A LLM powered agent playing wordle.

    This agent uses a ReAct loop with a tool to make guesses to a wordle
    game. Each agent plays independently, without communicating with
    other agents. It reports its logs to the UserAgent on the dashboard.
    """

    def __init__(self, user_agent_handle: Handle[UserAgent]) -> None:
        super().__init__(user_agent_handle=user_agent_handle)
        self.model = "claude-haiku-5-5"

    @action
    async def play_wordle(self, game: WordleGame) -> str:
        """Play a game of wordle."""

        @tool("wordle_feedback", game.make_guess.__doc__, {"guess": str})
        async def guess(args: dict[str, Any]) -> dict[str, Any]:
            text = str(game.make_guess(args["guess"]))
            return {"content": [{"type": "text", "text": text}]}

        options = ClaudeAgentOptions(
            model=self.model,
            system_prompt=(
                "You are playing Wordle, a word-guessing game. "
                "The target is a 5-letter English word. "
                "The `wordle_feedback` tool has an internal hidden word "
                "that you are trying to guess. "
                "Use the `wordle_feedback` tool to make guesses. "
                "After each guess you receive per-letter feedback: "
                "correct (right position), present (wrong position), "
                "absent (not in word). "
                "Use this feedback to narrow down the answer."
            ),
            mcp_servers={
                "wordle": create_sdk_mcp_server("wordle", tools=[guess]),
            },
            # Only expose our tools, not built-in or user-configured ones
            tools=[],
            strict_mcp_config=True,
            allowed_tools=["mcp__wordle__wordle_feedback"],
            max_turns=12,
        )

        result = ""
        async for message in query(
            prompt=(
                "Play wordle by guessing words using `wordle_feedback`. "
                "Return the answer to the wordle puzzle."
            ),
            options=options,
        ):
            if isinstance(message, ResultMessage):
                result = message.result or ""
        return result


async def main(user_agent_id: UUID):
    game = WordleGame()

    async with await Manager.from_exchange_factory(
        factory=HttpExchangeFactory(),
        log_config=recommended_logging(),
    ) as manager:
        # The agents report to your UserAgent on the dashboard
        user_agent_handle = manager.get_handle(
            AgentId(uid=user_agent_id, name="UserAgent"),
        )

        logger.info("Launching agents.")
        hdls = [
            await manager.launch(
                WordleAgent,
                kwargs={"user_agent_handle": user_agent_handle},
            )
            for _ in range(2)
        ]

        logger.info("Starting agent actions.")
        results = await asyncio.gather(
            *(hdl.play_wordle(game) for hdl in hdls),
        )
        for hdl, result in zip(hdls, results, strict=True):
            logger.info(f"{hdl.agent_id} returned {result}")

        logger.info(f"True target word: {game.target}")


if __name__ == "__main__":
    # Load USER_AGENT_ID from settings.env in the project root
    dotenv.load_dotenv(dotenv.find_dotenv("settings.env", usecwd=True))
    raise SystemExit(asyncio.run(main(UUID(os.environ["USER_AGENT_ID"]))))
