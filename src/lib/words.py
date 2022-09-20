from lib.geometry import Area


class Words:
    def __init__(self, words: 'Words' = None, area: Area = None):
        self.list = []
        assert (words is None and area is None) or (words is not None and area is not None), "word and area must be ether not set, or set together"
        if words is not None and area is not None:
            self.list = words.in_bound(area)
    
    def add(self, area: Area):
        self.list.append(area)
    
    def in_bound(self, area: Area):
        return [w for w in self.list if area.in_bound(area)]