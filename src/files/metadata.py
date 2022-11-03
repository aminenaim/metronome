import datetime
import os
import time
from urllib.parse import urlparse

import requests


class Metadata:
    __TIMESTR = '%a, %d %b %Y %X GMT'
    
    @staticmethod
    def is_local(url: str):
        url_parsed = urlparse(url)
        if url_parsed.scheme in ('file', ''): # Possibly a local file
            return os.path.exists(url_parsed.path)
        return False

    @staticmethod
    def check_update(source: str, destination: str, file_name: str) -> bool:
        if not os.path.exists(f'{destination}/{file_name}'):
            return True
        if Metadata.is_local(source):
            return Metadata.time_local(source) > Metadata.time_local(f'{destination}/{file_name}')        
        else:
            return Metadata.time_remote(source) > Metadata.time_local(f'{destination}/{file_name}') 
            

    @staticmethod
    def time_remote(url: str) -> datetime:
        request = requests.get(url, timeout=60)
        header = request.headers['last-modified']
        return datetime.datetime.strptime(header,Metadata.__TIMESTR)
    
    @staticmethod
    def time_local(path: str) -> datetime:
        timestamp = time.strftime(Metadata.__TIMESTR,time.gmtime(os.path.getmtime(path)))
        return datetime.datetime.strptime(timestamp,Metadata.__TIMESTR)
