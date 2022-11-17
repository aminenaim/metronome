import json
import os
from typing import Tuple

from jsonschema import validate


class Environnement:
   """Environnement class managing configuration and environnement variables
   """
   DEFAULT_CONFIG_PATH = "config/config.json"
   """Default config file
   """
   VALIDATION_CONFIG_FILE = "schema/config.json"
   """File where schema are stored
   """
   VARIABLES = ['level', 'detect', 'print', 'workdir', 'output', 'force', 'time']
   """list of used environnement variables
   """

   @classmethod
   def get_config(cls, file: str) -> dict:
      """Gather configuration keys and values from the config JSON file

      Args:
          file (str): file path

      Returns:
          dict: configuration elements
      """
      CONFIG = {}
      if not os.path.exists(file):
         return CONFIG
      else:
         with open(cls.VALIDATION_CONFIG_FILE) as validation_file, open(file) as json_file:
            json_object = json.load(json_file)
            validation_json = json.load(validation_file)
            validate(json_object, validation_json)
            CONFIG = json_object
         return CONFIG
         
   @classmethod
   def get_env(cls) -> dict:
      """Gather environnement variables

      Returns:
          dict: environnement variables
      """
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
   def get_parametters(cls, arguments: dict) -> Tuple[dict, dict, dict]:
      """Get parametters from all sources (cli, environnement and config file)

      Args:
          arguments (dict): cli arguments

      Returns:
          Tuple(dict, dict, dict): General, FTP and schedules parametters
      """
      ENV = Environnement.get_env()
      ENV.update(arguments)
      config_file = ENV['config'] if ('config' in ENV) else cls.DEFAULT_CONFIG_PATH
      CONFIG = Environnement.get_config(config_file)
      PARAMETTERS = CONFIG.copy()
      if 'ftp' not in PARAMETTERS:
         PARAMETTERS['ftp'] = []
      PARAMETTERS['general'].update(ENV)
      return PARAMETTERS['general'], PARAMETTERS['ftp'], PARAMETTERS['schedules']
