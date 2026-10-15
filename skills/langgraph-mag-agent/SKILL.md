---
name: langgraph-mag-agent
description: Use when building or debugging a LangGraph agent in this repo that calls an LLM through the AmSC Model Access Gateway (MAG) with ChatOpenAI, pauses for human approval, or runs a node on Aurora or another HPC endpoint with Globus Compute.
---

# Build LangGraph agents with the MAG and Globus Compute

The working example is `intermediate/02_langgraph/similar_molecules.py`:

```
START -> propose (LLM) -> confirm (human y/n) --y--> run_on_aurora (Globus Compute) -> summarize (LLM) -> END
                                              \--n--> END
```

## 1. Connect ChatOpenAI to the MAG

```python
dotenv.load_dotenv(dotenv.find_dotenv("settings.env", usecwd=True))


def get_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=os.environ["LLM_MODEL"],
        base_url=os.environ[
            "OPENAI_BASE_URL"
        ],  # https://mag.genesis.americansciencecloud.org/v1
        api_key=os.environ["AMSC_TOKEN"],
        # The hackathon project only has a google allocation on MAG.
        default_headers={"X-AmSC-MAG-Provider": "google"},
    )
```

- `settings.env` is in the repository root. Git ignores it. It holds `LLM_MODEL`, `OPENAI_BASE_URL`, and `AMSC_TOKEN`.
- Read the token with `os.environ["AMSC_TOKEN"]`. Do not use `.get()`. If the key is `None`, ChatOpenAI uses `OPENAI_API_KEY` and sends that key to the MAG.
- Always send the `X-AmSC-MAG-Provider` header.
- Make the LLM inside `get_llm()`, not at import time. Then the graph compiles without credentials.

## 2. Diagnose MAG errors

| Symptom | Cause | Action |
|---|---|---|
| `KeyError: 'AMSC_TOKEN'` | The token is not in `settings.env`. | Tell the user to add `AMSC_TOKEN=<key>` to `settings.env`. Do not ask for the token in chat. Do not put the token in a command line. A hook blocks inline credentials. |
| `403` with an HTML page "Cloudflare Access" (`is_warp: False`, `mtls_status: NONE`) | An access gate stopped the request before the MAG. The MAG did not examine the token or the model. | Tell the user to run `source utilities/mag_shell_util.sh && mag --list` in a terminal. If that also fails, the network or computer does not have access. See https://amsc-docs-d762d2.gitlab.io/model-access-gateway/. |

## 3. Get structured output

Use `get_llm().with_structured_output(PydanticModel, method="json_schema")`.
Make sure that the output is valid before you use it. For example, drop SMILES strings where `Chem.MolFromSmiles` returns `None`.

## 4. Ask for human approval before you use a shared system

Aurora, Perlmutter, and Frontier are shared. Pause the graph before a node submits work to them.

```python
def confirm(state):
    answer = interrupt({"endpoint": "Aurora", "molecules": state.molecules})
    return {"approved": str(answer).strip().lower() in ("y", "yes")}


builder.add_conditional_edges("confirm", route_after_confirm, ["run_on_aurora", END])
graph = builder.compile(
    checkpointer=InMemorySaver()
)  # interrupt() needs a checkpointer

config = {"configurable": {"thread_id": str(uuid.uuid4())}}
state = graph.invoke(MoleculeState(request=request), config)
while "__interrupt__" in state:
    print(state["__interrupt__"][0].value)
    state = graph.invoke(Command(resume=input("[y/N] ")), config)
```

## 5. Run a node with Globus Compute

**REQUIRED:** Use the `globus-compute-run` skill to select the endpoint and for its rules.
That skill also covers imports inside the function and the timeout on `result()`.

One more rule applies to graph nodes:

```python
with Executor(endpoint_id=os.environ["AURORA_ENDPOINT_ID"]) as ex:
    ex.serializer = ComputeSerializer(strategy_code=AllCodeStrategies())
    rows = ex.submit(compute_qed, state.molecules).result(timeout=300)
```

This rule is for Python functions. If you do not set the serializer, a function from an imported module is sent by reference.
Then the worker fails with `ModuleNotFoundError: No module named '<module>'`.
This occurs when you import the graph file, for example in a test.
It does not occur when you run the file as a script.

If an LLM writes a shell command, send the command as a value: `ShellFunction("{cmd}", walltime=60)` and `ex.submit(sh, cmd=command)`.
Do not put the command directly in the `ShellFunction` template. `ShellFunction` reads `{...}` in the template as a field, and commands from `awk` or `--format` contain braces.

Make sure that the endpoint ID is not empty before you start the graph. If it is empty, stop before you ask the user for approval.

A warning about different Python patch versions (for example 3.13.0 and 3.13.6) is not a problem.

## 6. Test the graph without the LLM

Replace the node functions on the module before you call `build_graph()`. Then do the `n` path and the `y` path:

```python
import similar_molecules as sm

sm.propose = lambda s: {"molecules": {"aspirin": "CC(=O)Oc1ccccc1C(=O)O"}}
sm.summarize = lambda s: {"summary": "stub"}
graph = sm.build_graph()
```

## Reference files

- `intermediate/02_langgraph/similar_molecules.py`: the full graph.
- `utilities/mag_shell_util.sh`: the MAG test with curl (`mag --list`).
