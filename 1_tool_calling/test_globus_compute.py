from globus_compute_sdk import Executor

compute_endpoint = '9a947ba5-f537-4681-acf3-cc66485aadec' # Polaris Globus Compute endpoint

POLARIS_CONFIG = {
    'account': 'ModCon',
    'queue': 'debug',
    'config_key': 'source /home/yadunand/setup_openmm.sh'
}

gce = Executor(endpoint_id=compute_endpoint, 
               user_endpoint_config=POLARIS_CONFIG)

def hello_world(name: str):
    import platform
    return f"Hello {name} from Polaris\n{list(platform.uname())}"

future = gce.submit(hello_world, "ModCon")

# Globus compute implements an asynchronous model.
# Block and wait for the result
print(future.result())
