import os
import ssl
from ftplib import FTP, FTP_TLS


class FtpHandler:
    def __init__(self, ftp_ident: dict):
        if 'ssl' in ftp_ident and ftp_ident['ssl']:
            context = ssl.create_default_context()
            self.conn = FTP_TLS(context=context)
        else:
            self.conn = FTP()
        self.conn.connect(host=ftp_ident['host'], port=ftp_ident['port'])
        self.conn.login(user=ftp_ident['user'], passwd=ftp_ident['password'])
        if 'folder' in ftp_ident:
            self.conn.cwd(ftp_ident['folder'])
    
    def send_file(self, file_name, src_folder="/"):
        dir_local = os.getcwd()
        os.chdir(src_folder)
        with open(file_name, 'rb') as fp:
            self.conn.storbinary('STOR ' + fp.name, fp)
        os.chdir(dir_local)
    
    def list(self):
        self.conn.retrlines('LIST')
    
    def close(self):
        self.conn.close()