import os
import sys, getopt
from lib.environnement import Environnement
from lib.pdf import Metadata, Pdf

VERSION = '1.0.0'

ENV = Environnement.get_parametters()
DATA = Environnement.get_data()

def version(): 
   print(VERSION)
   
def help():
   print("Help")
   
def parse():
   if 'URL' not in ENV:
      ENV['URL'] = DATA['URL'][ENV['LEVEL'].upper()]
   if ('FORCE' in ENV and not ENV['FORCE']) or Metadata.check_update(ENV['URL'],Pdf.PDF_NAME):
      print("Getting pdf images and words")
      courses = []
      pdf = Pdf(ENV['URL'] ,"tests/output")
      print("Processing image and words")
      pages = pdf.gen_pages()
      for page in pages:
         weeks = page.gen_weeks()
         for week in weeks:
            courses = courses + week.gen_courses()
            week.frame_elements()
            week.save("tests/output")
      courses.sort(key=lambda x: x.begin)
      for c in courses:
         print(c)
            
         
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