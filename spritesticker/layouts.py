'''
implements various layouts which controls image positioning
'''

from copy import copy
from itertools import groupby

from utils import lcm
from packing import SmallestWidthAlgorithm

__all__ = ['SpriteLayout', 'BoxLayout', 'RepeatXLayout']

class SpriteLayout(object):
    '''
    base class
    '''
    def __init__(self, images):
        self.size = 0, 0
        self.images = []
        self.fillCoef = 0
        self.extend(images)

    def _initStartupPlacement(self):
        imagePositions = []
        for im in self.images:
            rect = im.getOuterRect()
            im.displayRect = rect
            imagePositions.append(rect)
        return imagePositions

    def placeImages(self):
        raise NotImplementedError('this method is shold be overriden in the offsprings')

    def add(self, image):
        'add a image for appopriate CSS selector into container'
        if image.repeat != self.repeat:
            raise ValueError('%s can contain only %s images' % (self.__class__.__name__, self.repeat))
        self.images.append(image)

    def extend(self, images):
        for image in images:
            self.add(image)

    @property
    def placedImages(self):
        for im in self.images:
            yield im, im.displayRect

    @property
    def imagesCount(self):
        return len(self.images)

class BoxLayout(SpriteLayout):
    '''
    tries to squash images into compact area
    '''
    repeat = 'no-repeat'

    def placeImages(self):    
        rects = self._initStartupPlacement()        
        alg = SmallestWidthAlgorithm(rects)
        alg.compute()
        self.size = alg.size
        self.fillCoef = alg.fillingCoef
        
class RepeatXLayout(SpriteLayout):
    '''
    layout for images with repeat-x
    '''
    repeat = 'repeat-x'

    def add(self, image):
        if image.marginLeft != 0 or image.marginRight != 0:
            raise ValueError('x repeated images cannot have left or right margin')
        super(RepeatXLayout, self).add(image)

    def placeImages(self):
        rects = self._initStartupPlacement()
        width = reduce(lcm, [rect.width for rect in rects])
        if width > 5000:
            raise ValueError('generated image will have width %dpx, check inputs' % width)
        height = 0
        for rect in rects:
            rect.topleft = 0, height
            height += rect.height
            rect.width = width
        self.size = width, height

class RepeatYLayout(SpriteLayout):
    '''
    layout for images with repeat-y
    '''
    repeat = 'repeat-x'

    def add(self, image):
        if image.marginTop != 0 or image.marginBottom != 0:
            raise ValueError('x repeated images cannot have top or bottom margin')
        super(RepeatYLayout, self).add(image)

    def placeImages(self):
        rects = self._initStartupPlacement()
        height = reduce(lcm, [rect.height for rect in rects])
        if height > 5000:
            raise ValueError('generated image will have height %dpx, check inputs' % height)
        width = 0
        for rect in rects:
            rect.topleft = width, 0
            width += rect.width
            rect.height = height
        self.size = width, height

