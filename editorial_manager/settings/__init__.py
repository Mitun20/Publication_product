from dotenv import dotenv_values

config = dotenv_values(".env")
env = config.get('ENVIRONMENT','dev')

# Map the 'ENV' value to the corresponding settings module
settings_mapping = {
    'local': 'local',
    'dev': 'dev'
}

# Check if the environment is valid
if env not in settings_mapping:
    raise ValueError(f"Invalid environment '{env}' specified")

# Import the appropriate settings module based on the environment
settings_module = settings_mapping[env]

# Dynamically import settings
try:
    exec(f"from .{settings_module} import *")
except ImportError:
    raise ImportError(f"Could not import settings module: {settings_module}")
