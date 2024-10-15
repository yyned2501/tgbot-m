
import yaml  

with open('config_example/launch.yaml', 'r') as file:  
    data = yaml.safe_load(file)  

print(data)