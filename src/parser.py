import os, time, sys, getopt
import requests
import urllib
from lib.environnement import Environnement
from lib.ftp import ftp_handler
from lib.pdf import Metadata, Page, Pdf
from lib.week import Group, Week
from ics import Calendar, Event

VERSION = '1.0.0'
HELP = ("This script parse the well formed and very useful ( :D ) STRI pdf\n"
        "\n"
        "Options:\n"
        "   -w, --workdir=[WORKDIR]   temp folder used by the script\n"
        "   -o, --output=[OUTPUT]   output folder where ics are generated\n"
        "   -c, --config=[CONFIG]   config folder where config.json and data.json is located\n"
        "   -l, --level=[LEVELS]    levels that must be parsed (l3, m1, m2), must be seperated by comma\n"
        "   -d, --detect            show detected element of pdf\n"
        "   -p, --print             print classes genarated in stdout\n"
        "   -t, --time=[TIME]       use to loop each for the defined seconds\n"
        "   --force                 force parsing of pdf even if it's the same than remote\n"
        "   --ftp_test              test the ftp connexion\n"
        "   -h, --help              show helper for this script\n"
        "   --version               show version of script\n"
        "\n"
        "Runs on python3 with dependences listed on requirements.txt\n")

def version():
   """Print the verison of this script
   """
   print(VERSION)
   
def help():
   """Print the help string 
   """
   print(HELP)
   
def ftp_test():
   """Ftp connexion test provided by the user
      It also list the files on the current directory
   """
   ftp_ident = ENV['FTP']
   ftp = ftp_handler(ftp_ident)
   print("FTP Connexion OK")
   print("Listing files from current directory :")
   ftp.list()

def loop_time():
   """Loop for forever, with a delay of 'TIME' seconds (with TIME provided by the user through config/env/cli) 
   """
   delay = int(ENV['TIME'])
   print(f"Starting script, with refresh delay of {delay} sec")
   while(True):
      processing_levels()
      print(f"Waiting for {delay} sec")
      time.sleep(delay)
   
def processing_levels():
   """Process each level given by the user
   """
   workdir, output, urls, levels = ENV['WORKDIR'], ENV['OUTPUT'], DATA['URL'], ENV['LEVEL'].upper().split(',')
   mkdir_if_not_exists(workdir)
   for l in levels:
      l = l.replace(" ", "") # remove free space
      if l in urls.keys():
         print(f"Processing {l} pdf")
         parsing_edt(l, urls[l], workdir, output)
      else:
         print(f"Level {l} not found in data.json", file=sys.stderr)
         exit(1)

def parsing_edt(level: str, url: str, workdir: str, ics_dir: str):
   """Parse the edt into ics files and send them over ftp

   Args:
       level (str): level given by the user
       url (str): edt url of the given level
       workdir (str): script working directory
       ics_dir (str): ics output script
   """
   level_workdir = f"{workdir}/{level}"
   mkdir_if_not_exists(level_workdir)
   try: 
      if edt_need_update(url, level_workdir):
         print(f"{level} : Download and convert pdf into image and words")
         pdf = Pdf(url ,level_workdir)
         print(f"{level} : Processing and parsing images and words")
         pages = pdf.gen_pages()
         print(f"{level} : Gen weeks")
         weeks = gen_weeks(level_workdir, pages)
         print(f"{level} : Get courses")
         courses = gen_courses(level_workdir, weeks)
         print(f"{level} : Generate ics callendars")
         gen_calendars(courses, level, ics_dir)
         if ('FTP' in ENV):
            print(f"{level} : Sending files through ftp")
            send(level, ics_dir)
      else:
         print("Skiping, local pdf is older than remote pdf")
   except (requests.exceptions.ConnectionError, urllib.error.URLError):
      print("Connexion error")
      return

def edt_need_update(url : str, level_workdir : str) -> bool:
   """Define if the edt need an update :
      - when attribute 'FORCE' is used
      - when target pdf is newer than the local pdf

   Args:
       url (str): edt file url
       level_workdir (str): level working directory

   Returns:
       bool: True if edt need update, False otherwise
   """
   return ('FORCE' in ENV and ENV['FORCE']) or Metadata.check_update(url, level_workdir, Pdf.PDF_NAME)

def gen_weeks(level_workdir: str, pages: list) -> list:
   """Generate weeks from pages

   Args:
       level_workdir (str): level working directory
       pages (list): pages object of edt

   Returns:
       list: the weeks generated
   """
   weeks = []
   for page in pages:
      weeks += page.gen_weeks()
      if 'DETECT' in ENV and ENV['DETECT']:
         detect_words(page, f'{level_workdir}/detected')
   i = 0
   time_axe_ref = None
   while i <= len(weeks) and time_axe_ref is None: # get a reference 
      if len(weeks[i].time_axe):
         time_axe_ref = weeks[i].time_axe
      i+=1
   for week in weeks:
      if not len(week.time_axe) and time_axe_ref is not None:
         week.time_axe = time_axe_ref
   return weeks
   

def gen_courses(level_workdir: str, weeks: list) -> list:
   """Generate the courses from the pdf data

   Args:
       level_workdir (str): level working directory
       weeks (list): weeks object of edt

   Returns:
       list: list of the courses generated
   """
   courses = []
   for week in weeks:
      if 'DETECT' in ENV and ENV['DETECT']:
         detect_elements(week, f'{level_workdir}/detected')
      if len(week.days.list) and len(week.time_axe):  
         courses += week.gen_courses()
      else:
         print(f"Wrong Week detected with {len(week.days.list)} days and {len(week.hours.list)} hours")
   courses.sort(key=lambda x: x.begin)
   if 'PRINT' in ENV and ENV['PRINT']:
      print_courses(courses)
   return courses

def gen_calendars(courses: list, level: str, ics_dir: str):
   """Generate ics callendar using generated courses 

   Args:
       courses (list): generated courses from pdf
       level (str): course level
       ics_dir (str): ics directory
   """
   mkdir_if_not_exists(ics_dir)
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
      with open(f'{ics_dir}/{n}.ics', 'w') as f:
         f.write(str(calendar[g]))

def send(level: str, ics_folder: str):
   """Send generated ics files through ftp

   Args:
       level (str): course level
       ics_folder (str) : ics directory
   """
   ftp_ident = ENV['FTP']
   ftp = ftp_handler(ftp_ident)
   files = [f'{level}A', f'{level}G1', f'{level}G2', f'{level}E']
   for f in files:
      ftp.send_file(f'{f}.ics', ics_folder)
   ftp.close()

def detect_elements(week: Week, detect_folder: str):
   """Save detected elements on each week 

   Args:
       week (Week): processed week 
       detect_folder (str): folder which the file (with detected elements) should be saved
   """
   mkdir_if_not_exists(detect_folder)
   week.frame_elements()
   week.save(detect_folder)

def detect_words(page: Page, detect_folder: str):
   """Save detected element on each pages

   Args:
       page (Page): processed page
       detect_folder (str): folder wich the file (with detected elements) should be saved
   """
   mkdir_if_not_exists(detect_folder)
   page.frame_elements()
   page.save(detect_folder)

def print_courses(courses: list):
   """Print generated courses 

   Args:
       courses (list): generated courses
   """
   for c in courses:
      print(c)
      
def mkdir_if_not_exists(folder: str):
   """Create a folder if it doesn't extists

   Args:
       folder (str): folder which must be created/checked
   """
   if not os.path.exists(folder):
      print(f"Creating \"{folder}\" folder")
      os.makedirs(folder)

def main(argv : list):
   """Main function, Handle the cli arguments, gather environnement variables and config file parameters.
      This function also define which action to perfom

   Args:
       argv (list): list of argument and values pass by the user
   """
   global ENV, DATA
   ATTR = {}
   action = None
   options, _ = getopt.getopt(argv, 'w:o:c:u:l:t:dpvh', ['workdir=','output=', 'config=', 'url=', 'level=', 'time=', 'detect', 'print', 'force', 'ftp_test', 'help',  'version'])
   assign_map = {'-w':'WORKDIR', '--workdir':'WORKDIR', '-o':'OUTPUT', '--output':'OUTPUT', '-c':'CONFIG', '--config': 'CONFIG', '-u':'URL', '--url':'URL', '-l':'LEVEL', '--level':'LEVEL', '-d':'DETECT', '--detect':'DETECT', '-p':'PRINT', '--print':'PRINT', '--force':'FORCE', '-t':'TIME', '--time':'TIME'}
   action_map = {'--ftp_test':ftp_test, '-h':help, '--help':help, '--version':version} 
   for opt, arg in options:
      in_maps = False
      if opt in assign_map.keys():
         in_maps = True
         key = assign_map[opt]
         ATTR[key] = arg
      elif opt in action_map.keys():
         in_maps = True
         action = action_map[opt]
      if not in_maps:
         print(f"Unknown argument {opt}", file=sys.stderr)
         exit(1)
   
   ENV = Environnement.get_parametters(ATTR)
   DATA = Environnement.get_data(ATTR)
   if action is None:
      action = loop_time if ('TIME' in ENV) else processing_levels
   action()
   exit(0)

if __name__ == "__main__":
   main(sys.argv[1:])