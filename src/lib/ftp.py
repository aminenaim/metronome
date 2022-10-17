from array import ArrayType
from ftplib import FTP, FTP_TLS
from os import curdir
import os
import ssl


class ftp_handler:
    def __init__(self, ftp_ident: ArrayType):
        if 'SSL' in ftp_ident and ftp_ident['SSL']:
            context = ssl.create_default_context()
            self.conn = FTP_TLS(context=context)
        else:
            self.conn = FTP()
        self.conn.connect(host=ftp_ident['HOST'], port=ftp_ident['PORT'])
        self.conn.login(user=ftp_ident['USER'], passwd=ftp_ident['PASSWORD'])
    
    def send_file(self, file_name, src_folder="/", dest_folder="/"):
        dir_local = os.getcwd()
        dir_server = self.conn.pwd()
        os.chdir(src_folder)
        self.conn.cwd(dest_folder)
        with open(file_name, 'rb') as fp:
            self.conn.storbinary('STOR ' + fp.name, fp)
        self.conn.cwd(dir_server)
        os.chdir(dir_local)
    
    def list(self):
        self.conn.retrlines('LIST')
    
    def close(self):
        self.conn.close()