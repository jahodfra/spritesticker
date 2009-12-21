'''
implements packing problem approximation how for a set of rectangles choose the rect which will best cover them.
'''

def transpose(pair):
    x, y = pair
    return y, x

def findfirst(filter, iterable):
    for item in iterable:
        if filter(item):
            return item
    return None

class Rect(object):
    __slots__ = ['left', 'top', 'width', 'height']

    def __init__(self):
        self.left = 0
        self.top = 0
        self.width = 0
        self.height = 0

    def transpose(self):
        'transpose all coordinates'
        self.left, self.top = self.top, self.left
        self.width, self.height = self.height, self.width

    @property
    def area(self):
        return self.width * self.height
    
    def _get_size(self):
        return self.width, self.height
    def _set_size(self, val):
        self.width, self.height = val

    size = property(_get_size, _set_size)

    def _get_topleft(self):
        return self.left, self.top
    def _set_topleft(self, val):
        self.left, self.top = val

    topleft = property(_get_topleft, _set_topleft)

    @property
    def right(self): return self.left + self.width

    @property
    def bottom(self): return self.top + self.height

    @property
    def bottomright(self): return self.left + self.width, self.top + self.height

    @property
    def box(self): return self.topleft + self.bottomright

class AlgorithmError(RuntimeError): pass

class PackingAlgorithm:
    def __init__(self, rects):
        self.rects = rects
        self.size = 0, 0
        
    def compute(self):
        pass

    def minWidth(self):
        return max(rect.width for rect in self.rects)

    def minHeight(self):
        return max(rect.height for rect in self.rects)

    def minAreaBound(self):
        '''minArea >= minWidth * minHeight'''
        return sum(rect.area for rect in self.rects)

    def transpose(self):
        'transpose problem, it can be usefull for some positioning strategies'
        for rect in self.rects:
            rect.transpose()
        self.size = transpose(self.size)

    def shrinkSize(self):
        width =  max(rect.right for rect in self.rects)
        height = max(rect.bottom for rect in self.rects)
        self.size = width, height

class SmallestWidthAlgorithm(PackingAlgorithm):
    '''
    approximation which tries to fill rects into the rect with predefined width.
    '''
    def __init__(self, rects):
        PackingAlgorithm.__init__(self, rects)
        self.highest = 0
        self.actualX = 0
        self.actualY = 0

    def startNewRow(self):
        self.actualX = 0
        self.actualY = self.highest

    def placeRect(self, rect):
        rect.topleft = self.actualX, self.actualY
        self.actualX = rect.right
        self.highest = max(self.highest, rect.bottom)

    def compute(self, width=0):
        if width == 0:
            width = self.minWidth()
        self.sortRects()
        rects = self.rects[:]
        while rects:
            actualRect = findfirst(lambda rect: rect.width + self.actualX <= width, rects)
            if not actualRect:
                if self.actualX == 0:
                    raise AlgorithmError('algorithm cannot place any remaining rect to ensure predefined width')
                else:
                    self.startNewRow()
                    continue
            rects.remove(actualRect)
            self.placeRect(actualRect)
        self.size = width, self.highest
        return self.rects

    def sortRects(self):
        self.rects.sort(key=lambda item: item.height, reverse=True)

