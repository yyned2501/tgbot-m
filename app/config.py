import yaml

with open("config/launch.yaml", "r") as file:
    launch = yaml.safe_load(file)

with open("config/setting.yaml", "r") as file:
    setting = yaml.safe_load(file)