import sys
import yaml
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def load_config():
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)
