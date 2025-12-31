import yaml
import os

class ConfigLoader:
    def __init__(self, config_path="configs/config.yaml"):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.config_path = os.path.join(base_dir, config_path)
        self.config = self._load_config()

    def _load_config(self):
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Config file not found at: {self.config_path}")

        with open(self.config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def get(self, key, default=None):
        value = self.config
        for k in key.split("."):
            if not isinstance(value, dict):
                return default
            value = value.get(k, default)
        return value

config = ConfigLoader()
