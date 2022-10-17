import os
import json

class Environnement:
   VARIABLES = ['URL', 'LEVEL', 'DETECT', 'PRINT', 'FOLDER', 'OUTPUT', 'FTP', 'FORCE', 'TIME']
   
   @staticmethod
   def valid_config(file: str = "/config/config.json"):
      if not os.path.exists(file):
         return True
      with open(os.path.exists(file)) as jsonFile:
         try:
            json.load(jsonFile)
            jsonFile.close()
         except ValueError as err:
            return False
         return True

   @staticmethod
   def get_config(file: str):
      CONFIG = {}
      if not os.path.exists(file):
         return CONFIG
      else:
         with open(file) as json_file:
            json_object = json.load(json_file)
            json_file.close()
            for key in json_object:
               if key.upper() in Environnement.VARIABLES:
                  CONFIG[key] = json_object[key]
         return Environnement.__to_upper(CONFIG)
         
   @staticmethod
   def get_env():
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

   @staticmethod
   def get_parametters(file: str = "/config/config.json"):
      ENV = Environnement.get_env()
      CONFIG = Environnement.get_config(file)
      PARAMETTERS = CONFIG.copy()
      PARAMETTERS.update(ENV)
      return PARAMETTERS
   
   @staticmethod
   def get_data(file: str = "/config/data.json"):
      DATA = {}
      if not os.path.exists(file):
         return DATA
      else:
         with open(file) as json_file:
            json_object = json.load(json_file)
            json_file.close()
            for key in json_object:
               DATA[key.upper()] = json_object[key]
         return Environnement.__to_upper(DATA)

   @staticmethod
   def __to_upper(dictionary: dict) -> dict:
      upper_dict = {}
      for k,v in dictionary.items():
         if isinstance(v,dict):
            v = Environnement.__to_upper(v)
         upper_dict[k.upper()] = v
      return upper_dict