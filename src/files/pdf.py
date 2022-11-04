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
    """Class used to download and manipulate pdf
    """
    PDF_NAME = 'edt.pdf'
    """generic name of downloaded pdf
    """
    PAGE_NAME = 'page'
    """generic name of page images
    """
    
    def __init__(self, url: str, temp_dir: str) -> None:
        """Constructor of Pdf
        Download and convert it into jpeg pages 

        Args:
            url (str): url of pdf to be downloaded (or copied if it's a local file)
            temp_dir (str): working directory
        """
        self.temp_dir: str = temp_dir
        self.file: str = f'{temp_dir}/{self.PDF_NAME}'
        self.__fetch_file(url=url)
        self.pdf_pages =  pdf2image.convert_from_path(pdf_path=self.file, dpi=200)
        self.__save()
    
    def __save(self) -> None:
        """save each pdf page into an jpeg image
        """
        for i, p in enumerate(self.pdf_pages):
            p.save(f'{self.temp_dir}/{self.PAGE_NAME}{i}.jpg',"JPEG")

    def __fetch_file(self, url: str) -> None:
        """Fetch the file whether it is a local or remote file

        Args:
            url (str): file url
        """
        if Metadata.is_local(url):
            shutil.copyfile(src=url, dst=self.file)
        else:
            request.urlretrieve(url=url, filename=self.file)
    
    def gen_pages(self) -> List['Page']:
        """Generate each page of the pdf with an usable image and a list of words with coordinates

        Returns:
            List[Page]: list of generated pages
        """
        pages = [] 
        with open(self.file, "rb") as file:
            rsrcmgr = PDFResourceManager()
            laparams = LAParams()
            device = PDFPageAggregator(rsrcmgr=rsrcmgr, laparams=laparams)
            interpreter = PDFPageInterpreter(rsrcmgr=rsrcmgr, device=device)
            for page_number, page in enumerate(PDFPage.get_pages(fp=file)):
                image = Image(path=f'{self.temp_dir}/{self.PAGE_NAME}{page_number}.jpg')
                words = self.__fetch_words(area=image.area, interpreter=interpreter, device=device, page=page)
                page = Page(image=image, words=words, id=page_number)
                pages.append(page)
        return pages
        
    def del_pages(self) -> None:
        """deleted generated images of pages
        """
        for page_number in range(0,len(self)):
            os.remove(path=f'{self.temp_dir}/{self.PAGE_NAME}{page_number}.jpg')

    def __fetch_words(self, area: Area, interpreter: PDFPageInterpreter, device: PDFPageAggregator, page: PDFPage) -> AreaList:
        """Featch word on a given pdf page with it's coordinate

        Args:
            area (Area): image area of the page
            interpreter (PDFPageInterpreter): page interpreter 
            device (PDFPageAggregator): page aggregator
            page (PDFPage): page itself

        Returns:
            AreaList: list of area with word content
        """
        words = AreaList()
        interpreter.process_page(page=page)
        layout = device.get_result()
        for element in layout:
            if isinstance(element, LTTextBoxHorizontal):
                for text_line in element._objs:
                    t = tuple(e*(200/72) for e in text_line.bbox)
                    a = Area(p1=Point(int(t[0]),int(area.h() - t[3])), p2=Point(int(t[2]),int(area.h() - t[1])), content=text_line.get_text().strip())
                    words.append(a)
        return words
    
    def __len__(self) -> int:
        """Get the number of page

        Returns:
            int: number of pages
        """
        return len(self.pdf_pages)