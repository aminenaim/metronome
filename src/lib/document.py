import datetime
import shutil
import time
from typing import List
import pdf2image
from urllib import request
from urllib.parse import urlparse
import requests
import os
from pdfminer.layout import LAParams
from pdfminer.converter import PDFResourceManager, PDFPageAggregator
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.layout import LTTextBoxHorizontal

from lib.geometry import Area, AxeType, Point, Range, AreaList
from lib.image import Image
from lib.time import Time
from lib.schedule import Week

class Metadata:
    __TIMESTR = '%a, %d %b %Y %X GMT'
    
    @staticmethod
    def is_local(url: str):
        url_parsed = urlparse(url)
        if url_parsed.scheme in ('file', ''): # Possibly a local file
            return os.path.exists(url_parsed.path)
        return False

    @staticmethod
    def check_update(source: str, destination: str, file_name: str) -> bool:
        if not os.path.exists(f'{destination}/{file_name}'):
            return True
        if Metadata.is_local(source):
            return Metadata.time_local(source) > Metadata.time_local(f'{destination}/{file_name}')        
        else:
            return Metadata.time_remote(source) > Metadata.time_local(f'{destination}/{file_name}') 
            

    @staticmethod
    def time_remote(url: str) -> datetime:
        request = requests.get(url, timeout=60)
        header = request.headers['last-modified']
        return datetime.datetime.strptime(header,Metadata.__TIMESTR)
    
    @staticmethod
    def time_local(path: str) -> datetime:
        timestamp = time.strftime(Metadata.__TIMESTR,time.gmtime(os.path.getmtime(path)))
        return datetime.datetime.strptime(timestamp,Metadata.__TIMESTR)

class Pdf:
    PDF_NAME = 'edt.pdf'
    PAGE_NAME = 'page'
    MARGIN = Area(Point(0,0),Point(20,56))
    
    def __init__(self, url: str, temp_dir: str) -> None:
        self.temp_dir: str = temp_dir
        self.file: str = f'{temp_dir}/{self.PDF_NAME}'
        self.__download(url)
        self.pdf_pages =  pdf2image.convert_from_path(self.file,200)
        self.__save()
    
    def __save(self) -> None:
        for i, p in enumerate(self.pdf_pages):
            p.save(f'{self.temp_dir}/{self.PAGE_NAME}{i}.jpg',"JPEG")

    def __download(self, url: str) -> None:
        if Metadata.is_local(url):
            shutil.copyfile(url, self.file)
        else:
            request.urlretrieve(url, self.file)
    
    def gen_pages(self) -> List['Page']:
        pages = [] 
        with open(self.file, "rb") as file:
            rsrcmgr = PDFResourceManager()
            laparams = LAParams()
            device = PDFPageAggregator(rsrcmgr, laparams=laparams)
            interpreter = PDFPageInterpreter(rsrcmgr, device)
            for page_number, page in enumerate(PDFPage.get_pages(file)):
                image = Image(f'{self.temp_dir}/{self.PAGE_NAME}{page_number}.jpg')
                words = self.__gen_words(image.area, interpreter, device, page)
                page = Page(image, words, page_number)
                pages.append(page)
        return pages
        
    def del_pages(self) -> None:
        for page_number in range(0,len(self)):
            os.remove(f'{self.temp_dir}/{self.PAGE_NAME}{page_number}.jpg')

    def __gen_words(self, area: Area, interpreter: PDFPageInterpreter, device: PDFPageAggregator, page: PDFPage) -> AreaList:          
        words = AreaList()
        interpreter.process_page(page)
        layout = device.get_result()
        for element in layout:
            if isinstance(element, LTTextBoxHorizontal):
                for text_line in element._objs:
                    t = tuple(e*(200/72) for e in text_line.bbox)
                    a = Area(Point(int(t[0]),int(area.h() - t[3])), Point(int(t[2]),int(area.h() - t[1])), content=text_line.get_text().strip())
                    words.append(a)
        return words
    
    def __len__(self) -> int:
        return len(self.pdf_pages)

class Page:
    __RANGE_WEEK = Range(1900, 2200, AxeType.ABSCISSA)
    
    def __init__(self, image: Image , words: AreaList, id: int) -> None:
        self.image = image
        self.id = id
        self.words = words
        self.times = self.__gen_week_time()
        self.week_coordinate = self.image.find_contours(False, False, self.__RANGE_WEEK)

    def __gen_week_time(self) -> AreaList:
        times = self.words.match(pattern=Time.REGEX_WEEK, remove=True)
        for t in times:
            t.content = Time(t.content)
        return times
            
    def gen_weeks(self) -> List[Week]:
        weeks = []
        for c in self.week_coordinate:
            r: Range = c.to_range(AxeType.ORDINATE)
            times = []
            for t in self.times:
                if r.in_bound(t):
                    times.append(t.content)
            image = self.image.sub(c)
            # make sure there is contour around the week
            image.frame(image.area, color=(0,0,0), size=5)
            image.frame(image.area, color=0, size=5)
            week_word = self.words.contained(c)
            week_word.change_origin(c.p1)
            week = Week(image, week_word, times, weeks)
            weeks.append(week)
        return weeks

    def frame_elements(self) -> None:
        for a in self.words:
            self.image.frame(a)
        for a in self.week_coordinate:
            self.image.frame(a, (0,255,0))
    
    def save(self, path: str):
        self.image.save(path, f'page-{self.id}')