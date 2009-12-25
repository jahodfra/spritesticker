'''
implements packing problem approximation how for a set of rectangles choose the rect which will best cover them.
'''
from utils import transpose, findfirst   
from rect import Rect

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

    @property
    def fillingCoef(self):
        sheetArea = self.size[0] * self.size[1]
        return sum(rect.width * rect.height for rect in self.rects) / float(sheetArea)

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

