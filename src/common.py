import os
import yaml

current_path = os.path.dirname(os.path.abspath(__file__))
PARENT_PATH = os.path.dirname(current_path)

with open(f'{PARENT_PATH}/conf/conf.yml', 'r') as f:
    CONFIG = yaml.safe_load(f)