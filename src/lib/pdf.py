from array import ArrayType
import datetime
import time
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

from lib.geometry import Area, AxeType, Point, Range
from lib.image import Image
from lib.words import Words

class Pdf:
    PDF_NAME = 'edt.pdf'
    PAGE_NAME = 'page'
    
    def __init__(self, url: str, temp_dir: str) -> None:
        self.temp_dir: str = temp_dir
        self.file: str = f'{temp_dir}/{self.PDF_NAME}'
        request.urlretrieve(url,self.file)
        self.pages =  pdf2image.convert_from_path(self.file,200)
        self.__save()
        self.images = []
        for i in range(0,len(self)):
            self.images.append(Image(f'{self.temp_dir}/{self.PAGE_NAME}{i}.jpg', Area(Point(0,0),Point(20,56))))
        self.text = self.__get_file_words()
    
    def __save(self) -> None:
        for i, p in enumerate(self.pages):
            p.save(f'{self.temp_dir}/{self.PAGE_NAME}{i}.jpg',"JPEG")
            
    def get_word(self, page: int) -> Words:
        return self.text[page]
    
    def __get_file_words(self) -> ArrayType:
        pages_words = []
        with open(self.file, "rb") as file:
            rsrcmgr = PDFResourceManager()
            laparams = LAParams()
            device = PDFPageAggregator(rsrcmgr, laparams=laparams)
            interpreter = PDFPageInterpreter(rsrcmgr, device)
            
            for i, page in enumerate(PDFPage.get_pages(file)):
                pages_words.append(Words())
                interpreter.process_page(page)
                layout = device.get_result()
                area: Area = self.images[i].area
                for element in layout:
                    if isinstance(element, LTTextBoxHorizontal):
                        for text_line in element._objs:
                            t = tuple(e*(200/72) for e in text_line.bbox)
                            a = Area(Point(area.h() - t[0], area.w() - t[1]), Point(area.h() - t[2], area.w() - t[3]), content=text_line.get_text().strip())
                            pages_words[i].add(a)
        return pages_words
    
    def __len__(self) -> int:
        return len(self.pages)

class Page:
    __AVG_WEEK = 300
    __RANGE_WEEK = Range(1900, 2200, AxeType.ABSCISSA)
    
    def __init__(self, image: Image , words: Words) -> None:
        self.image = image
        self.words = words
    
    def get_weeks(self) -> ArrayType:
        weeks_coord = self.image.find_contours(False, False, self.__AVG_WEEK, self.__RANGE_WEEK)
        

class Metadata:
    __TIMESTR = '%a, %d %b %Y %X GMT'
    
    @staticmethod
    def is_local(url):
        url_parsed = urlparse(url)
        if url_parsed.scheme in ('file', ''): # Possibly a local file
            return os.path.exists(url_parsed.path)
        return False

    @staticmethod
    def check_update(source, destination) -> bool:
        if not os.path.exists(destination):
            return True
        if Metadata.is_local(source):
            return Metadata.time_local(source) > Metadata.time_local(destination)        
        else:
            return Metadata.time_remote(source) > Metadata.time_local(destination) 

    @staticmethod
    def time_remote(url) -> datetime:
        request = requests.get(url)
        header = request.headers['last-modified']
        return datetime.datetime.strptime(header,Metadata.__TIMESTR)
    
    @staticmethod
    def time_local(path) -> datetime:
        timestamp = time.strftime(Metadata.__TIMESTR,time.gmtime(os.path.getmtime(path)))
        return datetime.datetime.strptime(timestamp,Metadata.__TIMESTR)
        
    