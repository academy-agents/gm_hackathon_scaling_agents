# Tool Calling

This example shows how to use Globus Compute to call tools. In the examples, a decorator `gce_wrapper` sends each function call to Globus Compute and waits for the result. The LLM sees a usual Python function with a name, a docstring, and type hints. The LLM does not know that the function runs on an HPC system.

| File | What it does |
|---|---|
| `test_globus_compute.py` | Runs `hello_world` on the endpoint. Run this file first to test the endpoint. |
| `tool_calling_globus_compute.py` | Gives an LLM three tools: count primes, calculate molecular energy, and run an MD trajectory. The script asks one random question, and the LLM selects the tool to run. |

Note: compute_energy and compute_trajectory return mock values. To make real tools, replace them with real code, for example PySCF or OpenMM.

Before you run the scripts, change the compute_endpoint in both files to your endpoint UUID or use the Polaris Globus Compute endpoint. Update user_endpoint_config with approrpiate options for your endpoint. For example, for Polaris you need to set the account and queue for the example Polaris endpoint.

The examples use LangChain with the OpenAI API. Configure your tokens as follows: 

   ```bash
  export OPENAI_API_KEY=$AMSC_TOKEN
  export OPENAI_BASE_URL=https://mag.genesis.americansciencecloud.org/v1
  ```

Run the programs with uv:

 ```bash
  uv run python advanced/1_tool_calling/test_globus_compute.py
  uv run python advanced/1_tool_calling/tool_calling_globus_compute.py
```

The script uses the model gpt-oss-120b. To use a different model, change model in ChatOpenAI.

Challenge: Add a tool that calculates QED with RDKit, as in intermediate Module 1. Ask the LLM about the drug-likeness of aspirin.
