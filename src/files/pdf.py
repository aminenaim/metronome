import os
import shutil
from typing import List
from urllib import request

import pdf2image
from pdfminer.converter import PDFPageAggregator, PDFResourceManager
from pdfminer.layout import LAParams, LTTextBoxHorizontal
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfpage import PDFPage

from files import Image, Metadata, Page
from geometry import Area, AreaList, Point


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