import os
import ssl
from ftplib import FTP, FTP_TLS


class FtpHandler:
    """Class handling ftp operations
    """
    def __init__(self, config: dict):
        """Creation of ftp handler

        Args:
            config (dict): ftp parametters 
        """
        if 'ssl' in config and config['ssl']:
            context = ssl.create_default_context()
            self.conn = FTP_TLS(context=context)
        else:
            self.conn = FTP()
        self.conn.connect(host=config['host'], port=config['port'])
        self.conn.login(user=config['user'], passwd=config['password'])
        self.conn.voidcmd("NOOP")
        if 'folder' in config:
            self.conn.cwd(config['folder'])
    
    def send_file(self, file_name: str, src_folder: str ="/") -> None:
        """Send a file to the ftp server

        Args:
            file_name (str): file that should be sent
            src_folder (str, optional): folder in which file sould be sent. Defaults to "/".
        """
        dir_local = os.getcwd()
        os.chdir(src_folder)
        with open(file_name, 'rb') as fp:
            self.conn.storbinary('STOR ' + fp.name, fp)
        os.chdir(dir_local)
    
    def close(self):
        """Close ftp connexion
        """
        self.conn.close()