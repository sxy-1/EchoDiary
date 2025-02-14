import json
import os

CONFIG_FILE = './data/config/config.json'
DEFAULT_CONFIG = {
    "key_path": "./data/keys/"
}

def load_config(file_path):
    if not os.path.exists(file_path):
        # Create the file with default settings if it doesn't exist
        with open(file_path, 'w') as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        return DEFAULT_CONFIG
    else:
        # Load the existing config file
        with open(file_path, 'r') as f:
            print("config_info")
            return json.load(f)

def save_config(file_path, config):
    with open(file_path, 'w') as f:
        json.dump(config, f, indent=4)

def get_config_value(key):
    config = load_config(CONFIG_FILE)
    return config.get(key, None)

def set_config_value(key, value):
    config = load_config(CONFIG_FILE)
    config[key] = value
    save_config(CONFIG_FILE, config)

def delete_config_key(key):
    config = load_config(CONFIG_FILE)
    if key in config:
        del config[key]
        save_config(CONFIG_FILE, config)
        return True
    return False

def list_config():
    config = load_config(CONFIG_FILE)
    return config

# Initial load or create config file
config_info = load_config(CONFIG_FILE)

# Example usage
if __name__ == "__main__":
    # Set a config value
    set_config_value('interval', 30)
    set_config_value('new_key', 'new_value')

    # Get a config value
    interval = get_config_value('interval')
    print(f"Interval: {interval}")

    # List all config values
    config_list = list_config()
    print("Config List:", config_list)

    # Delete a config key
    if delete_config_key('new_key'):
        print("Key 'new_key' deleted.")
    else:
        print("Key 'new_key' not found.")

    # List all config values again
    config_list = list_config()
    print("Config List after deletion:", config_list)
