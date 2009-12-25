'''
FEATURES
    * multiple used images are placed into spritesheet only oncere
    * images can have image background
    * optional optimalization for IE6 (transparency issues)
    * on the fly generated PIL.Images can be added into spritesheet
    * integrated PNG optimizer

TODO:
    * testy
        * test repeat images
            * image generation
            * css generation
            * no images added
            * bad image type added
        * test no-repat images
            * image generation
            * css generation
            * no images added
            * bad image type added
        * testPacking (not overlapping, preserving size)
    * inform gracefully about not finding image
    * implement horizontal repeat
    * write setup.py for integration into python site-packages
    * enable adding images to corners and centers / 3x3 container
    * enable generating markup blocks

Refactorization:
    * divide SpriteSheet to SpriteSheet and SpriteLayout?
'''

import os
from copy import copy
from itertools import groupby
import tempfile

import PIL
from PIL import ImageColor, ImageDraw

from utils import lcm, prettySize
from packing import SmallestWidthAlgorithm
from draw import blitSurface
from rect import Rect

__all__ = ['SheetImage', 'SpriteSheet', 'VerticalSheet', 'CssWriter', 'setPngOptimizer', 'setImageFolder']

pngOptimizer = ''
imageFolder = ''

def setPngOptimizer(cmd):
    '''
    e.g pngcrush, pngnq, pngquant
    setPngOptimizer('pngcrush %s %s')
    '''
    global pngOptimizer
    pngOptimizer = cmd

def setImageFolder(path):
    global imageFolder
    imageFolder = path

class CssWriter:
    def __init__(self):
        self.selectorToImage = {}

    def extend(self, spriteSheet):
        for image in spriteSheet.transformedImages():
            if image.selector:
                self.add(image.selector, image)

    def add(self, selector, image):
        self.selectorToImage[selector] = image
            
    def write(self, filename, pathPrefix=''):
        self.pathPrefix = pathPrefix

        fout = file(filename, 'w')
        for selector, image in self.selectorToImage.items():
            self._writeImageCss(fout, selector, image)
        fout.close()

    def _writeImageCss(self, fout, selector, image):
        imagePath = self.pathPrefix + image.filename
        repeat = image.repeat
        color = image.color or ''
        pos = '%dpx %dpx' % image.pos
        fout.write('%(selector)s {background: %(color)s url(%(imagePath)s) %(repeat)s %(pos)s;}\n' % locals())

TOP, RIGHT, BOTTOM, LEFT = range(4)

class SheetImage:
    '''
    attributes:
        pos - shifting image in pixels from topleft corner of image (not including margin).
            Usefull for dynamicly positioning image in div. Used only for CSS generation
            and background positioning
        image - image filename or PIL.Image.Image object
        path - 
        margin - top, right, bottom, left margin values.
            it is used for reserving free space around image in sprite sheet.
            Image size + margin + abs(image position) should be greater than containing div size.
        color - physical size of image in imagefile
        background -
        repeat -
    '''
    _repeatDict = {
            'no-repeat': (False, False),
            'repeat-x': (True, False),
            'repeat-y': (False, True),
            'repeat': (True, True),
    }

    def __init__(self, image, margin=(0,0,0,0), pos=(0,0), color=None, background=None, repeat='no-repeat'):
        '''
            image can be filename or PIL.Image object
        '''
        if isinstance(image, PIL.Image.Image):
            self.filename = ''
            self.path = ''
            self._image = image
        elif isinstance(image, (str, unicode)):
            self.filename = image
            self.path = os.path.join(imageFolder, self.filename)
            self._image = PIL.Image.open(self.path)
        else:
            raise ValueError('unsupported value for image')
        self.margin = margin

        #CSS properties
        self.pos = pos
        self.color = color
        self.background = background
        self.selector = ''
        self.repeat = repeat

    def setBackground(self, image):
        self.background = image
        return self

    def setSelector(self, selector):
        self.selector = selector
        return self

    def canBeMergedWith(self, image):
        '''transitive, reflexive, symetric relation'''
        return self.filename and self.filename == image.filename and self.repeat == image.repeat and \
        self.color == image.color and self.background is image.background

    def mergeWith(self, image):
        '''two images with same filename can be merged together (one transformed to the other)
        '''
        self.margin = [max(self.margin[i], image.margin[i]) for i in xrange(4)]
        image.margin = self.margin

    def setOuterPos(self, pos):
        self.pos = (self.pos[0] - pos[0] - self.margin[LEFT],
                    self.pos[1] - pos[1] - self.margin[TOP])

    def getOuterRect(self):
        r = Rect()
        r.size = (self.margin[LEFT] + self._image.size[0] + self.margin[RIGHT],
                  self.margin[TOP] + self._image.size[1] + self.margin[BOTTOM])
        return r

    def _pasteColor(self, sheet, rect):
        if self.color is not None:
            r, g, b = ImageColor.getrgb(self.color)
            color = r, g, b, 255
            sheet.paste(color, rect.box)

    def _pasteBackground(self, sheet, rect):
        if self.background is not None:
            self.background.drawInto(sheet, rect)

    def drawInto(self, surface, rect):
        self._pasteColor(surface, rect)
        self._pasteBackground(surface, rect)

        repeatX, repeatY = self._repeatDict[self.repeat]
        pos = (rect.left + self.margin[LEFT] + self.pos[0],
               rect.top + self.margin[TOP] + self.pos[1])

        blitSurface(self._image, pos, surface, rect, repeatX, repeatY)

class BaseSpriteSheet:
    def __init__(self, name, images=None, matteColor=None, drawBackgrounds=True, mode='RGBA'):
        self.name = name
        self.mode = mode
        if matteColor:
            self.matteColor = ImageColor.getrgb(matteColor)
        else:
            self.matteColor = (255, 255, 255, 0)
        self.drawBackgrounds = drawBackgrounds
        self.size = 0, 0
        self.images = []
        self.imagePlacement = []
        self.fillCoef = 0

        self.extend(images)

    def add(self, image):
        'add a image for appopriate CSS selector into container'
        if image.repeat != self.repeat:
            raise ValueError('%s can contain only %s images' % (self.__class__.__name__, self.repeat))
        self.images.append(image)

    def extend(self, images):
        for image in images:
            self.add(image)

    def transformedImages(self):
        for rect, images in self.imagePlacement:
            for im in images:
                yield im
                
    def getSpriteSheetPath(self):
        return os.path.join(imageFolder, self._getFilename())

    def getSpriteSheetFilename(self):
        return self.name + '.png'

    def _groupSame(self, images):
        images = list(images)
        while images:
            imageA = images.pop()
            group = [imageA]
            newImages = []
            for imageB in images:
                if imageA is not imageB and imageA.canBeMergedWith(imageB):
                    group.append(imageB)
                else:
                    newImages.append(imageB)
            images = newImages
            yield imageA, group

    def _initStartupPlacement(self):
        fn = lambda image: (image.filename, image.color, image.repeat)
        images = [copy(im) for im in self.images]
        images.sort(key=fn)

        self.imagePlacement = []
        for filename, group in groupby(images, key=fn):
            for pivot, groupedImages in self._groupSame(group):
                for im in groupedImages:
                    if im is not pivot:
                        pivot.mergeWith(im)
                self.imagePlacement.append((pivot.getOuterRect(), groupedImages))

    def _placeImages(self):
        raise NotImplementedError('this method is shold be overriden in the offsprings')

    def write(self):
        self._initStartupPlacement()
        self._placeImages()
        if not self.drawBackgrounds:
            for im in self.images:
                im.background = None
        sheet = PIL.Image.new(self.mode, self.size, self.matteColor)

        for rect, group in self.imagePlacement:
            image = group[0]
            image.drawInto(sheet, rect)
            for im in group:
                im.setOuterPos(rect.topleft)
                im.filename = self._getFilename()
                im._image = sheet

        self.saveFile(sheet)
        self.printInfo()

    def _getFilename(self):
        return self.name + '.png'

    def saveFile(self, sheet):
        path = self.getSpriteSheetPath()
        if pngOptimizer:
            tmpfile = tempfile.NamedTemporaryFile(suffix='png').name
            sheet.save(tmpfile, 'PNG')
            os.system(pngOptimizer % (tmpfile, path))
            os.remove(tmpfile)
        else:
            sheet.save(path, optimize=True)

    def printInfo(self):
        self._printBaseInfo()
        self._printSizeInfo()

    def _printBaseInfo(self):
        nImages = len(self.imagePlacement)
        print 'generating %s containing %d images' % (self._getFilename(), nImages)
        print '  dimension %d x %dpx' % self.size
        print '  requests saved %d' % (nImages - 1)
    
    def _printSizeInfo(self):
        placedImages = [images[0] for rect, images in self.imagePlacement]
        newsize = os.path.getsize(self.getSpriteSheetPath())
        if all(image.path != '' for image in placedImages):
            origsize = sum(os.path.getsize(image.path) for image in placedImages)
            sizeCoef = float(newsize) / origsize * 100.0
            print '  original images filesize: %s' % prettySize(origsize)
            print '  spritesheet filesize: %s (%.2f%%)' % (prettySize(newsize), sizeCoef)
        else:
            print '  spritesheet filesize: %s' % prettySize(newsize)

class SpriteSheet(BaseSpriteSheet):
    repeat = 'no-repeat'

    def printInfo(self):
        self._printBaseInfo()
        print '  filling coeficient is %.2f%%' % (self.fillCoef * 100.0)
        self._printSizeInfo()
    
    def _placeImages(self):
        rects = [rect for rect, group in self.imagePlacement]
        alg = SmallestWidthAlgorithm(rects)
        rects = alg.compute()
        self.size = alg.size
        self.fillCoef = alg.fillingCoef

class VerticalSheet(BaseSpriteSheet):
    repeat = 'repeat-x'

    def add(self, image):
        if image.margin[LEFT] != 0 or image.margin[RIGHT] != 0:
            raise ValueError('x repeated images cannot have left or right margin')
        BaseSpriteSheet.add(self, image)

    def _placeImages(self):
        rects = [rect for rect, group in self.imagePlacement]
        width = reduce(lcm, [rect.width for rect in rects])
        if width > 5000:
            raise ValueError('generated image will have width %dpx, check inputs' % width)
        height = 0
        for rect in rects:
            rect.topleft = 0, height
            height += rect.height
            rect.width = width
        self.size = width, height

