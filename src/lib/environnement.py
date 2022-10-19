import os
import json
from jsonschema import validate


class Environnement:
   DEFAULT_CONFIG_PATH = "config/"
   VALIDATION_FOLDER = "schema/"
   VARIABLES = ['URL', 'LEVEL', 'DETECT', 'PRINT', 'WORKDIR', 'OUTPUT', 'FTP', 'FORCE', 'TIME']
   
   @classmethod
   def valid_config(cls, file):
      if not os.path.exists(file):
         return True
      with open(os.path.exists(file)) as jsonFile:
         try:
            json.load(jsonFile)
            jsonFile.close()
         except ValueError as err:
            return False
         return True

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
            for key in json_object:
               if key.upper() in Environnement.VARIABLES:
                  CONFIG[key] = json_object[key]
         return Environnement.__to_upper(CONFIG)
         
   @classmethod
   def get_env(cls):
      ENV = {}
      for v in Environnement.VARIABLES:
         value =  os.getenv(v)
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
      config_file = ATTR["CONFIG"] if ('CONFIG' in ATTR) else cls.DEFAULT_CONFIG_PATH
      ENV = Environnement.get_env()
      CONFIG = Environnement.get_config(f'{config_file}/config.json')
      PARAMETTERS = CONFIG.copy()
      PARAMETTERS.update(ENV)
      PARAMETTERS.update(ATTR)
      return PARAMETTERS
   
   @classmethod
   def get_data(cls, ATTR: dict):
      data_file = ATTR["CONFIG"] if ('CONFIG' in ATTR) else cls.DEFAULT_CONFIG_PATH
      DATA = {}
      if not os.path.exists(f'{data_file}/data.json'):
         return DATA
      else:
         with open(f'{cls.VALIDATION_FOLDER}/data.json') as validation_file, open(f'{data_file}/data.json') as json_file:
            validation_json = json.load(validation_file)
            json_object = json.load(json_file)
            validate(json_object, validation_json)
            for key in json_object:
               DATA[key.upper()] = json_object[key]
         return Environnement.__to_upper(DATA)

   @classmethod
   def __to_upper(cls, dictionary: dict) -> dict:
      upper_dict = {}
      for k,v in dictionary.items():
         if isinstance(v,dict):
            v = Environnement.__to_upper(v)
         upper_dict[k.upper()] = v
      return upper_dict