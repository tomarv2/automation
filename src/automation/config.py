from starlette.config import Config

env = '.env'
config = Config(env)
#
LOG_LEVEL = "DEBUG"
#CONFIG_YAML_FILE ='/Users/varun.tomar/Documents/personal_github/mauto/src/automation/config.yaml'
CONFIG_YAML_FILE = config("CONFIG_YAML_FILE")
REQUIREMENTS_YAML_FILE = config("REQUIREMENTS_YAML_FILE")
USER_INPUT_ENV = config("USER_INPUT_ENV")
ROUTE_NOTIFICATION = config("ROUTE_NOTIFICATION")
RECIEVER_NOTIFICATION = config("RECIEVER_NOTIFICATION")
EA_RULES = config("EA_RULES")
PROMETHEUS_CONFIG = config("PROMETHEUS_CONFIG")
