'''
TODO:
    * draw repeated background ...QA
    * refactorize image merge ...OK
    * enable turning off optimalization for IE6 ...OK
    * enable adding PIL.Images into stylesheet ...OK
    * integrate PNG optimizer ...OK

    * inform gracefully about not finding image
    * implement horizontal repeat
    * write setup.py for integration into python site-packages
    * enable adding images to corners and centers / 3x3 container
    * ensure that repeat images are not placed into bad containers
    * enable generating markup blocks
    * umoznit volat write vickrat po sobe

Refactorization:
    * rename SpriteSheet to SpriteLayout?
Errors:
    * merged image can have outdated position parameters
'''

import os
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
        for selector, image in spriteSheet.getStyles():
            self.add(selector, image)

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
        return self.filename and self.filename == image.filename and self.repeat == image.repeat and \
        self.color == image.color and self.background is image.background

    def mergeWith(self, image):
        '''two images with same filename can be merged together (one transformed to the other)
        '''
        if self is image:
            return
        print 'merging', self.filname, image.filename
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
        self.placedImages = []

        images = images or []
        for image in images:
            self.add(image)

    def add(self, image):
        'add a image for appopriate CSS selector into container'
        image.repeat = self.repeat
        self.images.append(image)

    def getStyles(self):
        return [(im.selector, im) for im in self.images if im.selector]
                
    def getSpriteSheetPath(self):
        return os.path.join(imageFolder, self.name + '.png')

    def getSpriteSheetFilename(self):
        return self.name + '.png'

    def _uniqueImages(self, group):
        group = list(group)
        while group:
            imageA = group.pop()
            newGroup = []
            for imageB in group:
                if imageA.canBeMergedWith(imageB):
                    imageA.mergeWith(imageB)
                else:
                    newGroup.append(imageB)
            group = newGroup
            yield imageA

    def _getMergedImages(self):
        fn = lambda image: image.filename
        images = self.images[:]
        images.sort(key=fn)

        uniqueImages = [image
            for filename, group in groupby(images, key=fn)
            for image in self._uniqueImages(group)
        ]
        return uniqueImages

    def _getStartupConfiguration(self):
        unplacedImages = []
        for image in self._getMergedImages():
            rect = image.getOuterRect()
            unplacedImages.append((image, rect))
        return unplacedImages

    def _placeImages(self):
        unplacedImages = self._getStartupConfiguration()
        rects = map(lambda item: item[1], unplacedImages)
        self._placeRects(rects)
        self.placedImages = unplacedImages

    def _placeRects(self, rects):
        raise NotImplementedError('this method is shold be overriden in the offsprings')

    def write(self):
        self._placeImages()

        if self.drawBackgrounds:
            for im in self.images:
                im.background = None

        sheet = PIL.Image.new(self.mode, self.size, self.matteColor)

        for image, rect in self.placedImages:
            image.drawInto(sheet, rect)
            image.setOuterPos(rect.topleft)
            image.filename = self.name + '.png'
            image._image = sheet

        self.saveFile(sheet)
        self.printInfo()

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
        sheetArea = self.size[0] * self.size[1]
        fillCoef = sum(rect.width * rect.height for image, rect in self.placedImages) / float(sheetArea)
        nImages = len(self.placedImages)
        newsize = os.path.getsize(self.getSpriteSheetPath())
        if all(image.path != '' for image, rect in self.placedImages):
            origsize = sum(os.path.getsize(image.path) for image, rect in self.placedImages)
            sizeCoef = float(newsize) / origsize * 100.0
        else:
            origsize = -1

        print 'generating %s containing %d images' % (self.name + '.pdf', nImages)
        print '  dimension %d x %dpx' % self.size
        print '  filling coeficient is %.2f%%' % (fillCoef * 100.0)
        if origsize > 0:
            print '  original images filesize: %s' % prettySize(origsize)
            print '  spritesheet filesize: %s (%.2f%%)' % (prettySize(newsize), sizeCoef)
        else:
            print '  spritesheet filesize: %s' % prettySize(newsize)
        print '  requests saved %d' % (nImages - 1)

class SpriteSheet(BaseSpriteSheet):
    repeat = 'no-repeat'

    def _placeRects(self, rects):
        alg = SmallestWidthAlgorithm(rects)
        rects = alg.compute()
        self.size = alg.size

class VerticalSheet(BaseSpriteSheet):
    repeat = 'repeat-x'

    def add(self, image):
        if image.margin[LEFT] != 0 or image.margin[RIGHT] != 0:
            raise ValueError('x repeated images cannot have left or right margin')
        BaseSpriteSheet.add(self, image)

    def _placeRects(self, rects):
        width = reduce(lcm, [rect.width for rect in rects])
        height = 0
        for rect in rects:
            rect.topleft = 0, height
            height += rect.height
            rect.width = width
        self.size = width, height

