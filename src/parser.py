import ftplib
import getopt
import os
import sys
import time
import urllib
from typing import List

import requests

from files import Metadata, Page, Pdf
from schedule import Course, Week, EdtCalendar
from utils import Environnement, FtpHandler

VERSION = '1.3.1'
HELP = ("This script parses a pdf schedule.\n"
        "\n"
        "Options:\n"
        "   -w, --workdir=[WORKDIR]   temp folder used by the script\n"
        "   -o, --output=[OUTPUT]   output folder where ics are generated\n"
        "   -c, --config=[CONFIG]   config folder where config.json and data.json is located\n"
        "   -d, --detect            show detected element of pdf\n"
        "   -p, --print             print classes genarated in stdout\n"
        "   -t, --time=[TIME]       run this script in a loop for every TIME seconds\n"
        "   --force                 force parsing of pdf even if it's the same than remote\n"
        "   -h, --help              show helper for this script\n"
        "   --version               show version of script\n"
        "\n"
        "Runs on python3 with dependences listed on requirements.txt\n")

def version() -> None:
   """Print the verison of this script
   """
   print(VERSION)
   
def help() -> None:
   """Print the help string 
   """
   print(HELP)

def loop_time() -> None:
   """Loop for forever, with a delay of 'TIME' seconds (with TIME provided by the user through config/env/cli) 
   """
   delay = int(GENERAL['time'])
   print(f"Starting script, with refresh delay of {delay} sec")
   while(True):
      processing_levels()
      print(f"Waiting for {delay} sec")
      time.sleep(delay)
   
def processing_levels() -> None:
   """Process each level given by the user
   """
   workdir: str = GENERAL['workdir'] 
   output: str = GENERAL['output']
   mkdir_if_not_exists(workdir)
   for schedule, value in SCHEDULES.items():
      print(f"Processing {schedule} pdf")
      parsing_edt(schedule, value['url'], workdir, output)

def parsing_edt(level: str, url: str, workdir: str, ics_dir: str) -> None:
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
         pdf.del_pages()
         print(f"{level} : Gen weeks from {len(pages)} pages")
         weeks = gen_weeks(level_workdir, pages)
         print(f"{level} : Get courses from {len(weeks)} weeks")
         courses = gen_courses(level_workdir, weeks)
         print(f"{level} : Generate ics callendars from {len(courses)} courses")
         files_name = gen_calendars(courses, level, ics_dir)
         if len(FTP):
            print(f"{level} : Sending files through ftp")
            send(files_name, ics_dir)
      else:
         print("Skiping, local pdf is older than remote pdf")
   except (requests.exceptions.ConnectionError, urllib.error.URLError, ftplib.error_reply, ftplib.error_temp, ftplib.error_perm, ftplib.error_proto):
      print("Connexion error")
      delete_if_exists(f"{level_workdir}/{Pdf.PDF_NAME}") 
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
   return ('force' in GENERAL and GENERAL['force']) or Metadata.check_update(url, f'{level_workdir}/{Pdf.PDF_NAME}')

def gen_weeks(level_workdir: str, pages: List[Page]) -> List[Week]:
   """Generate weeks from pages

   Args:
       level_workdir (str): level working directory
       pages (list): pages object of edt

   Returns:
       list: the weeks generated
   """
   weeks: List[Week] = []
   for page in pages:
      weeks += page.gen_weeks()
      if 'detect' in GENERAL and GENERAL['detect']:
         detect_words(page, f'{level_workdir}/detected')
   i = 0
   time_axe_ref = None
   while i < len(weeks) and time_axe_ref is None: # get a reference 
      if len(weeks[i].hours.time_axe):
         time_axe_ref = weeks[i].hours
      i+=1
   for week in weeks:
      if not len(week.hours.time_axe) and time_axe_ref is not None:
         week.hours = time_axe_ref
   return weeks
   

def gen_courses(level_workdir: str, weeks: List[Week]) -> List[Course]:
   """Generate the courses from the pdf data

   Args:
       level_workdir (str): level working directory
       weeks (list): weeks object of edt

   Returns:
       list: list of the courses generated
   """
   courses: List[Course] = []
   for week in weeks:
      if 'detect' in GENERAL and GENERAL['detect']:
         detect_elements(week, f'{level_workdir}/detected')
      if len(week.days) and len(week.hours.time_axe):  
         courses += week.gen_courses()
      else:
         print(f"Wrong Week detected with {len(week.days)} days and {len(week.hours)} hours")
   courses.sort(key=lambda x: x.begin)
   if 'print' in GENERAL and GENERAL['print']:
      print_courses(courses)
   return courses

def gen_calendars(courses: List[Course], level: str, ics_dir: str) -> List[str]:
   """Generate ics callendar using generated courses 

   Args:
       courses (list): generated courses from pdf
       level (str): course level
       ics_dir (str): ics directory
      
   Returns:
       list: list of the files names generated
   """
   mkdir_if_not_exists(ics_dir)
   print(f"{level} : Generating Callendars")
   alt = SCHEDULES[level]['alt'] if 'alt' in SCHEDULES[level] else ''
   calendar = EdtCalendar(courses, level, alt)
   calendar.save(directory=ics_dir)
   return calendar.get_files_name()

def send(files_name: List[str], ics_folder: str) -> None:
   """Send generated ics files through ftp

   Args:
       level (str): course level
       ics_folder (str) : ics directory
   """
   for session in FTP:
      ftp = FtpHandler(session)
      for fn in files_name:
         ftp.send_file(fn, ics_folder)
      ftp.close()

def detect_elements(week: Week, detect_folder: str) -> None:
   """Save detected elements on each week 

   Args:
       week (Week): processed week 
       detect_folder (str): folder which the file (with detected elements) should be saved
   """
   mkdir_if_not_exists(detect_folder)
   week.frame_elements()
   week.save(detect_folder)

def detect_words(page: Page, detect_folder: str) -> None:
   """Save detected element on each pages

   Args:
       page (Page): processed page
       detect_folder (str): folder wich the file (with detected elements) should be saved
   """
   mkdir_if_not_exists(detect_folder)
   page.frame_elements()
   page.save(detect_folder)

def print_courses(courses: List[Course]) -> None:
   """Print generated courses 

   Args:
       courses (list): generated courses
   """
   for c in courses:
      print(c)
      
def mkdir_if_not_exists(folder: str) -> None:
   """Create a folder if it doesn't exists

   Args:
       folder (str): folder which must be created/checked
   """
   if not os.path.exists(folder):
      print(f"Creating \"{folder}\" folder")
      os.makedirs(folder)

def delete_if_exists(file: str) -> None:
   """Delete a file if it exists

   Args:
       file (str): file to delete
   """
   if os.path.exists(file):
      os.remove(file)

def main(argv : list):
   """Main function, Handle the cli arguments, gather environnement variables and config file parameters.
      This function also define which action to perfom

   Args:
       argv (list): list of argument and values pass by the user
   """
   global GENERAL, FTP, SCHEDULES
   ATTR = {}
   action = None
   options, _ = getopt.getopt(argv, 'w:o:c:u:l:t:dpvh', ['workdir=','output=', 'config=', 'url=', 'level=', 'time=', 'detect', 'print', 'force', 'help',  'version'])
   assign_map = {'-w':'workdir', '--workdir':'workdir', '-o':'output', '--output':'output', '-c':'config', '--config': 'config', '-d':'detect', '--detect':'detect', '-p':'print', '--print':'print', '--force':'force', '-t':'time', '--time':'time'}
   action_map = {'-h':help, '--help':help, '--version':version} 
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
   
   GENERAL, FTP, SCHEDULES = Environnement.get_parametters(ATTR)
   if action is None:
      action = loop_time if ('time' in GENERAL) else processing_levels
   action()
   exit(0)

if __name__ == "__main__":
   main(sys.argv[1:])