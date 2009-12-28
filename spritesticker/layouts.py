from copy import copy
from itertools import groupby

from utils import lcm
from packing import SmallestWidthAlgorithm

__all__ = ['SpriteLayout', 'BoxLayout', 'RepeatXLayout']

class SpriteLayout(object):
    def __init__(self, images):
        self.size = 0, 0
        self.images = []
        self.imageGroups = []
        self.imagePositions = []
        self.fillCoef = 0
        self.extend(images)

    def _initStartupPlacement(self):
        self.imageGroups = mergeImages(self.images)
        self.imagePositions = []
        for group in self.imageGroups:
            self.imagePositions.append(group[0].getOuterRect())

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
        for i, images in enumerate(self.imageGroups):
            for im in images:
                yield im, self.imagePositions[i]

    @property
    def placedUniqueImages(self):
        for i, images in enumerate(self.imageGroups):
            yield images[0], self.imagePositions[i]

    @property
    def uniqueImagesCount(self):
        return len(self.imageGroups)

class BoxLayout(SpriteLayout):
    repeat = 'no-repeat'

    def placeImages(self):    
        self._initStartupPlacement()
        alg = SmallestWidthAlgorithm(self.imagePositions)
        alg.compute()
        self.size = alg.size
        self.fillCoef = alg.fillingCoef
        
class RepeatXLayout(SpriteLayout):
    repeat = 'repeat-x'

    def add(self, image):
        if image.marginLeft != 0 or image.marginRight != 0:
            raise ValueError('x repeated images cannot have left or right margin')
        super(RepeatXLayout, self).add(image)

    def placeImages(self):
        self._initStartupPlacement()
        rects = self.imagePositions
        width = reduce(lcm, [rect.width for rect in rects])
        if width > 5000:
            raise ValueError('generated image will have width %dpx, check inputs' % width)
        height = 0
        for rect in rects:
            rect.topleft = 0, height
            height += rect.height
            rect.width = width
        self.size = width, height

def mergeImages(images):
    def extractImageFromGroup(imageA, images):
        group = [imageA]
        newImages = []
        for imageB in images:
            if imageA is not imageB and imageA.canBeMergedWith(imageB):
                group.append(imageB)
            else:
                newImages.append(imageB)
        return group, newImages

    def groupSameImages(images):
        images = list(images)
        while images:
            imageA = images.pop()
            group, images = extractImageFromGroup(imageA, images)
            yield imageA, group

    fn = lambda image: (image.filename, image.color, image.repeat)
    images = [copy(im) for im in images]
    images.sort(key=fn)

    imageGroups = []
    for filename, group in groupby(images, key=fn):
        for pivot, groupedImages in groupSameImages(group):                
            for im in groupedImages:
                if im is not pivot:
                    pivot.mergeWith(im)
                imageGroups.append(groupedImages)
    return imageGroups

