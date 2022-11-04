import datetime
import os
import time
from urllib.parse import urlparse

import requests


class Metadata:
    """Class used to check the metadata between too files
    """
    __TIMESTR = '%a, %d %b %Y %X GMT'
    """Time format 
    """
    
    @staticmethod
    def is_local(url: str) -> bool:
        """Check if the given path target a local or remote file and exsists

        Args:
            url (str): file url

        Returns:
            bool: True if the file exists and is local, False otherwise
        """
        url_parsed = urlparse(url=url)
        if url_parsed.scheme in ('file', ''): # Possibly a local file
            return os.path.exists(path=url_parsed.path)
        return False

    @staticmethod
    def check_update(source: str, destination: str) -> bool:
        """Check if the source is older than the destination (and exists)

        Args:
            source (str): reference file path
            destination (str): file path to check

        Returns:
            bool: True if the file exists and is local, False otherwise
        """
        if not os.path.exists(path=destination):
            return True
        elif Metadata.is_local(source=source):
            return Metadata.time_local(path=source) > Metadata.time_local(path=destination)        
        else:
            return Metadata.time_remote(path=source) > Metadata.time_local(path=destination) 

    @staticmethod
    def time_remote(url: str) -> datetime:
        """Get the last modification datetime of a remote file

        Args:
            url (str): file url

        Returns:
            datetime: timestamp of last modification
        """
        request = requests.get(url=url, timeout=60)
        header = request.headers['last-modified']
        return datetime.datetime.strptime(header,Metadata.__TIMESTR)
    
    @staticmethod
    def time_local(path: str) -> datetime:
        """Get the last modification datetime of a local file

        Args:
            url (str): file path

        Returns:
            datetime: timestamp of last modification
        """
        timestamp = time.strftime(Metadata.__TIMESTR,time.gmtime(os.path.getmtime(path)))
        return datetime.datetime.strptime(timestamp,Metadata.__TIMESTR)
