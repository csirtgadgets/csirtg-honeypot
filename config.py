import yaml
import os

DEFAULT_CONFIG = os.path.expanduser("~/.wf.yml")


def config(fn=DEFAULT_CONFIG):
    if os.path.exists(fn):
        with open(fn, 'r') as f:
            return yaml.load(f)
    else:
        return None