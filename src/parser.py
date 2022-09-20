import os
import sys, getopt
from lib.environnement import Environnement
from lib.pdf import Metadata, Pdf

# http://pymotw.com/2/getopt/

OS_VAR = {'URL':os.getenv('URL')
          , 'VERBOSE':os.getenv('URL'),}

VERSION = '1.0.0'

ENV: dict = Environnement.get_parametters()
DATA: dict = Environnement.get_data()

def version(): 
   print(VERSION)
   
def help():
   print("Help")
   
def parse():
   print(DATA)
   if 'URL' not in ENV:
      ENV['URL'] = DATA['URL'][ENV['LEVEL']]
   print(ENV)
   if ('FORCE' in ENV and not ENV['FORCE']) or Metadata.check_update(ENV['URL'],Pdf.PDF_NAME):
      print("Parsing pdf into ics format")
      pdf = Pdf(ENV['URL'] ,"tests/output")
   else:
      print("Skiping, downloaded pdf is older than remote pdf, use --force to ignore that verification")


def main(argv):
   global ENV
   
   action = parse
   options, remainder = getopt.getopt(argv, 'f:o:u:vh', ['folder=','output=', 'url=', 'verbose', 'help',  'version'])

   for opt, arg in options:
      if opt in ('-f', '--folder'):
         ENV['FOLDER'] = arg
      if opt in ('-o', '--output'):
         ENV['OUTPUT'] = arg
      elif opt in ('-u', '--url'):
         ENV['URL'] = arg
      elif opt in ('--force'):
         ENV['FORCE'] = True
      elif opt in ('-v', '--verbose'):
         ENV['VERBOSE'] = True
      elif opt in ('-h', '--help'):
         action = help
      elif opt == '--version':
         action = version
   action()

if __name__ == "__main__":
   main(sys.argv[1:])