import new
import os
import tempfile

import PIL
from PIL import ImageColor, ImageDraw

from utils import prettySize
from draw import blitSurface
from rect import Rect

__all__ = ['SheetImage', 'SpriteSheet', 'CssWriter', 'setPngOptimizer', 'setImageFolder']

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
        for image in spriteSheet.transformedImages:
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

    @property
    def leftMargin(self):
        return margin[self.LEFT]
    
    @property
    def rightMargin(self):
        return margin[self.RIGHT]

    @property
    def rightMargin(self):
        return margin[self.RIGHT]

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
        self.pos = (self.pos[0] - pos[0] - self.marginLeft,
                    self.pos[1] - pos[1] - self.marginTop)

    def getOuterRect(self):
        r = Rect()
        r.size = (self.marginLeft + self._image.size[0] + self.marginRight,
                  self.marginTop + self._image.size[1] + self.marginBottom)
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
        pos = (rect.left + self.marginLeft + self.pos[0],
               rect.top + self.marginTop + self.pos[1])

        blitSurface(self._image, pos, surface, rect, repeatX, repeatY)

for i, name in enumerate(('Top', 'Right', 'Bottom', 'Left')):
    setattr(SheetImage, 'margin'+name, property(fget=lambda self: self.margin[i]))
        
class SpriteSheet:
    def __init__(self, name, layout, matteColor=None, drawBackgrounds=True, mode='RGBA'):
        self.name = name
        self.mode = mode
        if matteColor:
            self.matteColor = ImageColor.getrgb(matteColor)
        else:
            self.matteColor = (255, 255, 255, 0)
        self.drawBackgrounds = drawBackgrounds
        self.layout = layout

    def getSpriteSheetPath(self):
        return os.path.join(imageFolder, self.getSpriteSheetFilename())
    
    def getSpriteSheetFilename(self):
        return self.name + '.png'

    def write(self):
        self.layout.placeImages()
        sheet = PIL.Image.new(self.mode, self.layout.size, self.matteColor)

        for im, rect in self.layout.placedUniqueImages:
            if not self.drawBackgrounds:
                im.background = None
            im.drawInto(sheet, rect)

        self._saveFile(sheet)
        self._printInfo()

    def _saveFile(self, sheet):
        path = self.getSpriteSheetPath()
        if pngOptimizer:
            tmpfile = tempfile.NamedTemporaryFile(suffix='png').name
            sheet.save(tmpfile, 'PNG')
            os.system(pngOptimizer % (tmpfile, path))
            os.remove(tmpfile)
        else:
            sheet.save(path, optimize=True)
    
    @property
    def transformedImages(self):
        for image, rect in self.layout.placedImages:
            image.setOuterPos(rect.topleft)
            image.filename = self.getSpriteSheetFilename()
            yield image

    def _printInfo(self):
        self._printBaseInfo()
        self._printSizeInfo()

    def _printBaseInfo(self):
        nImages = self.layout.uniqueImagesCount
        print 'generating %s containing %d images' % (self.getSpriteSheetFilename(), nImages)
        print '  dimension %d x %dpx' % self.layout.size
        print '  requests saved %d' % (nImages - 1)
        print '  filling coeficient is %.2f%%' % (self.layout.fillCoef * 100.0)
    
    def _printSizeInfo(self):
        placedImages = list(self.layout.placedUniqueImages)
        newsize = os.path.getsize(self.getSpriteSheetPath())
        if all(image.path != '' for image, rect in placedImages):
            origsize = sum(os.path.getsize(image.path) for image, rect in placedImages)
            sizeCoef = float(newsize) / origsize * 100.0
            print '  original images filesize: %s' % prettySize(origsize)
            print '  spritesheet filesize: %s (%.2f%%)' % (prettySize(newsize), sizeCoef)
        else:
            print '  spritesheet filesize: %s' % prettySize(newsize)

