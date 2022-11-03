from copy import deepcopy
from datetime import timedelta
from typing import List

from files import Image
from geometry import Area, AreaList, Axe, AxeType, Point, Range


class Hours:
    def __init__(self, words_hours: AreaList, words_id: AreaList, margin : Range, week_image: Image) -> None:
        self.image = self.__get_image(words_hours, words_id, margin, week_image)
        lines = self.__detect_time_scale()
        hour_axe = self.__get_hours_axe(words_hours, lines, margin)
        self.time_axe = self.__get_time_axe(lines, hour_axe)
    
    def __get_image(self, words_hours: AreaList, words_id: AreaList, margin : Range, week_image: Image) -> Image:
        image = None
        if len(words_hours):
            hour_area = Area(Point(margin.a, words_hours.first().y1()), Point(margin.b, words_hours.first().y2()))
            image = week_image.sub(hour_area)
            upper_words_hours = deepcopy(words_hours)
            upper_words_id = deepcopy(words_id)
            upper_words_hours.change_origin(hour_area.p1)
            upper_words_id.change_origin(hour_area.p1)
            for wd in upper_words_hours:
                image.frame(wd, 255, -1)
            for wi in upper_words_id:
                image.frame(wi, 255, -1)
        return image
            
    def __detect_time_scale(self) -> List[int]:
        lines = []
        if self.image is not None:
            one_d = self.image.one_dimension(True)
            i = 0
            while i < len(one_d):
                if one_d[i] < 150:
                    lines.append(i)
                    while i < len(one_d) and one_d[i] < 200 :
                        i+=1
                else:
                    i+=1
        return lines
    
    def __get_hours_axe(self, words_hours: AreaList, lines: List[int], margin: Range) -> Axe:
        hour_axe = Axe()
        words_hours.sort(key=lambda wh: wh.p1.x)
        if len(words_hours):
            hour = int(words_hours.first().content.replace('h','')) - 1
            hour_axe.add(margin.a, hour)
        for wh in words_hours:
            hour = int(wh.content.replace('h',''))
            middle = wh.middle(AxeType.ABSCISSA)
            i = -1
            while((i + 1) < len(lines) and lines[i + 1] < middle):
                i+=1
            hour_axe.add(lines[i], hour)
        if len(words_hours):
            self.__add_last_hour(words_hours, lines, hour_axe)
        return hour_axe
    
    def __add_last_hour(self, words_hours: AreaList, lines: List[int], hour_axe: Axe):
        hour = int(words_hours.last().content.replace('h','')) + 1
        list_hour = list(hour_axe)
        lenght_previous_hour = abs(list_hour[len(list_hour) - 2] - list_hour[len(list_hour) - 1])
        lenght_current_hour = abs(list_hour[len(list_hour) - 1] - lines[len(lines) - 1])
        if abs(lenght_previous_hour - lenght_current_hour) > abs(lenght_previous_hour/2 - lenght_current_hour):
            lines.append(lines[len(lines) - 1] + int(lenght_current_hour/2)) # Add last quarter
            lines.append(lines[len(lines) - 1] + int(lenght_current_hour)) # Add last hour
            hour_axe.add(lines[len(lines) - 1] + int(lenght_current_hour), hour) 
        else:
            hour_axe.add(lines[len(lines) - 1], hour)
    
    def __get_time_axe(self, lines: List[int], hour_axe: Axe):
        list_key = list(hour_axe)
        time_axe = Axe()
        matrice_hour = self.__sublist_hour(lines, list_key)
        for lst in matrice_hour:
            hour = hour_axe[lst[0]]
            if len(lst) == 3:
                lst.insert(1, int((lst[0] + lst[1])/2))
            elif len(lst) != 4 and len(lst) != 1:
                nexts = [l for l in lines if l > lst[len(lst) - 1]]
                if len(nexts):
                    step = (nexts[0] - lst[0])/4
                    lst = [int(lst[0] + i*step) for i in range(0,4)]
            for id, element in enumerate(lst):
                time_axe.add(element, timedelta(hours=hour, minutes=15*id))
        return time_axe
    
    def __sublist_hour(self, lines: List[int], list_key: List[int]):
        matrice_hour: List[List[int]] = []
        id_key,id_line = 0,0
        while(id_key + 1 < len(list_key)):
            matrice_hour.append([lines[id_line]])
            id_line+=1
            while(id_line < len(lines) and lines[id_line] < list_key[id_key + 1]):
                matrice_hour[id_key].append(lines[id_line])
                id_line+=1
            id_key+=1
        if id_line < len(lines):
            matrice_hour.append([])
        while(id_line < len(lines)):
            matrice_hour[id_key].append(lines[id_line])
            id_line+=1

        return matrice_hour    