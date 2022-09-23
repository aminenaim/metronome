import os
import sys, getopt
from lib.environnement import Environnement
from lib.pdf import Metadata, Pdf
from lib.week import Group, Week
from ics import Calendar, Event

VERSION = '1.0.0'

ENV = Environnement.get_parametters()
DATA = Environnement.get_data()

def version(): 
   print(VERSION)
   
def help():
   print("Help")
   
def parse():
   if not os.path.exists(ENV['FOLDER']):
      print(f"Creating \"{ENV['FOLDER']}\" folder")
      os.makedirs(ENV['FOLDER'])
   levels = ENV['LEVEL'].upper().split(',')
   for l in levels:
      if l in DATA['URL'].keys():
         print(f"Processing {l} pdf")
         process(l, DATA['URL'][l], ENV['FOLDER'], ENV['OUTPUT'])
      else:
         print(f"{l} not found in data.json")

def process(level: str, url: str, path: str, output: str):
   folder = f"{path}/{level}"
   if not os.path.exists(folder):
      print(f"Creating \"{folder}\" folder")
      os.makedirs(folder)
   if ('FORCE' in ENV and ENV['FORCE']) or Metadata.check_update(url, folder, Pdf.PDF_NAME):
      print(f"{level} : Parsing pdf into images and words")
      courses = []
      pdf = Pdf(url ,folder)
      print(f"{level} : Processing image and words")
      pages = pdf.gen_pages()
      for page in pages:
         weeks = page.gen_weeks()
         if 'DETECT' in ENV and ENV['DETECT']:
            detect_words(page, f'{folder}/detected')
         for week in weeks:
            courses = courses + week.gen_courses()
            if 'DETECT' in ENV and ENV['DETECT']:
               detect_elements(week, f'{folder}/detected')
      courses.sort(key=lambda x: x.begin)
      if 'PRINT' in ENV and ENV['PRINT']:
         print_courses(courses)
      gen_calendars(courses, level, output)
   else:
      print("Skiping, downloaded pdf is older than remote pdf, use --force to ignore that verification")

def gen_calendars(courses, level, folder):
   if not os.path.exists(folder):
      print(f"Creating \"{folder}\" folder")
      os.makedirs(folder)
   print(f"{level} : Generating Callendars")
   calendar = {Group.ALL:Calendar(), Group.GROUP1:Calendar(), Group.GROUP2:Calendar()}
   name = {Group.ALL:f'{level}', Group.GROUP1:f'{level}G1', Group.GROUP2:f'{level}G2'}
   for c in courses:
      call: Calendar = calendar[c.group]
      e = Event(name=c.name, description=c.teacher, location=c.location, begin=c.begin, end=c.end)
      call.events.add(e)
   for g, n in name.items():
      print(f"{level} : Creating {n}.ics")
      with open(f'{folder}/{n}.ics', 'w') as f:
         f.write(str(calendar[g]))

def detect_elements(week: Week, folder: str):
   if not os.path.exists(folder):
      print(f"Creating \"{folder}\" folder")
      os.makedirs(folder)
   week.frame_elements()
   week.save(folder)

def detect_words(page: Week, folder: str):
   if not os.path.exists(folder):
      print(f"Creating \"{folder}\" folder")
      os.makedirs(folder)
   page.frame_words()
   page.save(folder)

def print_courses(courses):
   for c in courses:
      print(c)


def main(argv):
   global ENV
   
   action = parse
   options, remainder = getopt.getopt(argv, 'f:o:u:l:dpvh', ['folder=','output=', 'url=', 'level=', 'detect', 'print', 'force', 'verbose', 'help',  'version'])

   for opt, arg in options:
      if opt in ('-f', '--folder'):
         ENV['FOLDER'] = arg
      if opt in ('-o', '--output'):
         ENV['OUTPUT'] = arg
      elif opt in ('-u', '--url'):
         ENV['URL'] = arg
      elif opt in ('-l', '--level'):
         ENV['LEVEL'] = arg
      elif opt in ('-d', '--detect'):
         ENV['PRINT'] = arg
      elif opt in ('-p', '--print'):
         ENV['PRINT'] = True
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