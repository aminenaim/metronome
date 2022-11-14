import json
import os

from jsonschema import validate


class Environnement:
   DEFAULT_CONFIG_PATH = "config/config.json"
   VALIDATION_FOLDER = "schema/"
   VARIABLES = ['level', 'detect', 'print', 'workdir', 'output', 'force', 'time']

   @classmethod
   def get_config(cls, file: str):
      CONFIG = {}
      if not os.path.exists(file):
         return CONFIG
      else:
         with open(f'{cls.VALIDATION_FOLDER}/config.json') as validation_file, open(file) as json_file:
            json_object = json.load(json_file)
            validation_json = json.load(validation_file)
            validate(json_object, validation_json)
            CONFIG = json_object
         return CONFIG
         
   @classmethod
   def get_env(cls):
      ENV = {}
      for v in Environnement.VARIABLES:
         value =  os.getenv(v.upper())
         if value is not None:
            if value.lower() == 'true':
               ENV[v] = True
            elif value.lower() == 'false':
               ENV[v] = False
            else:
               ENV[v] = value
      return ENV

   @classmethod
   def get_parametters(cls, ATTR: dict):
      ENV = Environnement.get_env()
      ENV.update(ATTR)
      config_file = ENV['config'] if ('config' in ENV) else cls.DEFAULT_CONFIG_PATH
      print(ENV)
      CONFIG = Environnement.get_config(config_file)
      PARAMETTERS = CONFIG.copy()
      if ('general' in PARAMETTERS) and isinstance(PARAMETTERS['general'], dict):
         PARAMETTERS['general'].update(ENV)
      else:
         PARAMETTERS['general'] = ENV
      return PARAMETTERS
