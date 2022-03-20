import os
import json

#Create env variables
if os.path.exists("env.json"):
    with open("env.json", "r") as f:
        envs = json.loads(f.read())
        for env, var in envs.items():
            os.environ[env] = var