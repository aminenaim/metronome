from array import ArrayType
import os, time, sys, getopt
from lib.environnement import Environnement
from lib.ftp import ftp_handler
from lib.pdf import Metadata, Page, Pdf
from lib.week import Group, Week
from ics import Calendar, Event

VERSION = '1.0.0'
HELP = ("This script parse the well formed and very useful (lol) STRI pdf\n"
        "\n"
        "Options:\n"
        "   -f, --folder=[FOLDER]   temp folder used by the script\n"
        "   -o, --output=[OUTPUT]   output folder where ics are generated\n"
        "   -u, --url=[URL]         url of edt that must be parsed (when -l, --level is not provided)\n"
        "   -l, --level=[LEVELS]    levels that must be parsed (l3, m1, m2), must be seperated by comma\n"
        "   -d, --detect            show detected element of pdf\n"
        "   -p, --print             print classes genarated in stdout\n"
        "   -t, --time=[TIME]       use to loop each for the defined seconds"
        "   --force                 force parsing of pdf even if it's the same than remote\n"
        "   --ftp_test              test the ftp connexion\n"
        "   -h, --help              show helper for this script\n"
        "   --version               show version of script\n"
        "\n"
        "Runs on python3 with dependences listed on requirements.txt\n")


ENV = Environnement.get_parametters()
DATA = Environnement.get_data()

def version(): 
   print(VERSION)
   
def help():
   print(HELP)
   
def ftp_test():
   ftp_ident = ENV['FTP']
   ftp = ftp_handler(ftp_ident)
   print("FTP Connexion OK")
   print("Listing files from current directory :")
   ftp.list()

def loop_time():
   delay = int(ENV['TIME'])
   print(f"Starting script, with refresh delay of {delay} sec")
   while(True):
      parse()
      print(f"Waiting for {delay} sec")
      time.sleep(delay)
   
def parse():
   if not os.path.exists(ENV['FOLDER']):
      print(f"Creating \"{ENV['FOLDER']}\" folder")
      os.makedirs(ENV['FOLDER'])
   levels = ENV['LEVEL'].upper().split(',')
   for l in levels:
      l = l.replace(" ", "")
      if l in DATA['URL'].keys():
         print(f"Processing {l} pdf")
         process_edt(l, DATA['URL'][l], ENV['FOLDER'], ENV['OUTPUT'])
      else:
         print(f"{l} not found in data.json", file=sys.stderr)
         exit(1)

def process_edt(level: str, url: str, path: str, output: str):
   folder = f"{path}/{level}"
   if not os.path.exists(folder):
      print(f"Creating \"{folder}\" folder")
      os.makedirs(folder)
   if ('FORCE' in ENV and ENV['FORCE']) or Metadata.check_update(url, folder, Pdf.PDF_NAME):
      print(f"{level} : Parsing pdf into images and words")
      pdf = Pdf(url ,folder)
      print(f"{level} : Processing image and words")
      pages = pdf.gen_pages()
      courses = gen_courses(folder, pages)
      gen_calendars(courses, level, output)
      if ('FORCE' in ENV):
         print(f"{level} : Sending files trought ftp")
         send(level, output)
   else:
      print("Skiping, downloaded pdf is older than remote pdf, use --force to ignore that verification")

def gen_courses(folder: str, pages: ArrayType):
   courses = []
   for page in pages:
      weeks = page.gen_weeks()
      if 'DETECT' in ENV and ENV['DETECT']:
         detect_words(page, f'{folder}/detected')
      for week in weeks:
         if 'DETECT' in ENV and ENV['DETECT']:
            detect_elements(week, f'{folder}/detected')
         courses = courses + week.gen_courses()
   courses.sort(key=lambda x: x.begin)
   if 'PRINT' in ENV and ENV['PRINT']:
      print_courses(courses)
   return courses

def gen_calendars(courses, level, folder):
   if not os.path.exists(folder):
      print(f"Creating \"{folder}\" folder")
      os.makedirs(folder)
   print(f"{level} : Generating Callendars")
   grp_name = {Group.ALL:'All', Group.GROUP1:'Groupe 1', Group.GROUP2:'Groupe 2'}
   calendar = {Group.ALL:Calendar(), Group.GROUP1:Calendar(), Group.GROUP2:Calendar(), 'Exam':Calendar()}
   name = {Group.ALL:f'{level}A', Group.GROUP1:f'{level}G1', Group.GROUP2:f'{level}G2', 'Exam':f'{level}E'}
   for c in courses:
      if c.exam:
         grp = grp_name[c.group]
         call: Calendar = calendar['Exam']
         e = Event(name=c.name, description='Prof: ' + c.teacher + ' - ' + grp, location=c.location, begin=c.begin, end=c.end)         
      else:
         call: Calendar = calendar[c.group]
         e = Event(name=c.name, description='Prof: ' + c.teacher, location=c.location, begin=c.begin, end=c.end)
      call.events.add(e)
   for g, n in name.items():
      print(f"{level} : Creating {n}.ics")
      with open(f'{folder}/{n}.ics', 'w') as f:
         f.write(str(calendar[g]))

def send(level, folder):
   ftp_ident = ENV['FTP']
   ftp = ftp_handler(ftp_ident)
   files = [f'{level}A', f'{level}G1', f'{level}G2', f'{level}E']
   for f in files:
      ftp.send_file(f'{f}.ics', folder)
   ftp.close()

def detect_elements(week: Week, folder: str):
   if not os.path.exists(folder):
      print(f"Creating \"{folder}\" folder")
      os.makedirs(folder)
   week.frame_elements()
   week.save(folder)

def detect_words(page: Page, folder: str):
   if not os.path.exists(folder):
      print(f"Creating \"{folder}\" folder")
      os.makedirs(folder)
   page.frame_elements()
   page.save(folder)

def print_courses(courses):
   for c in courses:
      print(c)

def main(argv):
   global ENV
   
   action = loop_time if ('TIME' in ENV) else parse
   options, _ = getopt.getopt(argv, 'f:o:u:l:t:dpvh', ['folder=','output=', 'url=', 'level=', 'time=', 'detect', 'print', 'force', 'ftp_test', 'help',  'version'])

   for opt, arg in options:
      if opt in ('-f', '--folder'):
         ENV['FOLDER'] = arg
      if opt in ('-o', '--output'):
         ENV['OUTPUT'] = arg
      elif opt in ('-u', '--url'):
         ENV['URL'] = arg
      elif opt in ('-l', '--level'):
         ENV['LEVEL'] = arg
      elif opt in ('-t', '--time'):
         action = help
      elif opt in ('-d', '--detect'):
         ENV['DETECT'] = arg
      elif opt in ('-p', '--print'):
         ENV['PRINT'] = True
      elif opt in ('--force'):
         ENV['FORCE'] = True
      elif opt in ('--ftp_test'):
         ENV['TIME'] = True
         action = ftp_test
      elif opt in ('-h', '--help'):
         action = help
      elif opt == '--version':
         action = version
      else:
         print(f"Unknown argument {opt}", file=sys.stderr)
         exit(1)
   action()
   exit(0)

if __name__ == "__main__":
   main(sys.argv[1:])