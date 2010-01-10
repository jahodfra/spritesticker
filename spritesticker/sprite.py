'''
base module
'''

import new
import os
import tempfile

import PIL
from PIL import ImageColor, ImageDraw

from utils import prettySize
from draw import blitSurface
from rect import Rect

__all__ = ['SheetImage', 'SpriteSheet', 'CssWriter', 'setPngOptimizer', 'setImageFolder']

_pngOptimizer = ''
_imageFolder = ''

def setPngOptimizer(cmd):
    '''
    set a png optimizer command
    which is called on generated spritesheets

    e.g. pngcrush, pngnq, pngquant can be used
    setPngOptimizer('pngcrush %s %s')
    '''
    global _pngOptimizer
    _pngOptimizer = cmd

def setImageFolder(path):
    '''
    set a path to image folder
    simplifies the path definition for SpriteSheets and SheetImages
    '''
    global _imageFolder
    _imageFolder = path

class CssWriter:
    def __init__(self):
        self.selectorToImage = {}

    def register(self, spriteSheet):
        for image in spriteSheet.transformedImages:
            if image.selector:
                self.selectorToImage[selector] = image

    def write(self, filename, pathPrefix=''):
        '''
        writes out CSS file
        pathPrefix - path prefix for spritesheets images in css file
        '''
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
    Object representing properties of image which should be placed into spritesheet
    also represents properties for css generation

    attributes:
        path - full path to image file
        _image - PIL.Image.Image object
        see SheetImage.__init__
        ...
    '''
    _repeatDict = {
            'no-repeat': (False, False),
            'repeat-x': (True, False),
            'repeat-y': (False, True),
            'repeat': (True, True),
    }

    def __init__(self, image, margin=(0,0,0,0), pos=(0,0), color=None, background=None, selector='', repeat='no-repeat'):
        '''
        image can be filename or PIL.Image object
        pos - shifting image in pixels from topleft corner of image (not including margin).
              Usefull for dynamicly positioning image in div. Used only for CSS generation
              and background positioning
        image  - image filename on ImagePath or PIL.Image.Image
        margin - top, right, bottom, left margin values
                 it is used for reserving free space around image in sprite sheet.
                 Image size + margin + abs(image position) should be greater than containing div size.
        color, repeat - counterpart of same CSS property
        '''
        if isinstance(image, PIL.Image.Image):
            self.filename = ''
            self.path = ''
            self._image = image
        elif isinstance(image, (str, unicode)):
            self.filename = image
            self.path = os.path.join(_imageFolder, self.filename)
            self._image = PIL.Image.open(self.path)
        else:
            raise ValueError('unsupported value for image')
        self.margin = margin

        #CSS properties
        self.selector = selector
        self.color = color
        self.background = background
        self.pos = pos
        self.repeat = repeat

    def canBeMergedWith(self, image):
        '''
        two images differing only in pos and margin can be merged together
        (transitive, reflexive, symetric relation)
        '''
        return self.filename and self.filename == image.filename and self.repeat == image.repeat and \
        self.color == image.color and self.background is image.background

    def mergeWith(self, image):
        '''
        unifies both image margin
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

    def drawInto(self, surface, rect):
        self._pasteColor(surface, rect)
        self._pasteBackground(surface, rect)

        repeatX, repeatY = self._repeatDict[self.repeat]
        pos = (rect.left + self.marginLeft + self.pos[0],
               rect.top + self.marginTop + self.pos[1])

        blitSurface(self._image, pos, surface, rect, repeatX, repeatY)
    
    def _pasteColor(self, sheet, rect):
        if self.color is not None:
            r, g, b = ImageColor.getrgb(self.color)
            color = r, g, b, 255
            sheet.paste(color, rect.box)

    def _pasteBackground(self, sheet, rect):
        if self.background is not None:
            self.background.drawInto(sheet, rect)


for i, name in enumerate(('Top', 'Right', 'Bottom', 'Left')):
    pname = 'margin' + name
    getter = lambda self: self.margin[i]
    setattr(SheetImage, pname, property(fget=getter))
        
class SpriteSheet:
    def __init__(self, name, layout, matteColor=None, drawBackgrounds=True, mode='RGBA'):
        '''
        name - filename without suffix
        matteColor - bakckground color for generated stylesheet
        drawBackgrounds - toggle background images drawing
        mode - is a PIL.Image.mode for generated image ('RGB' or 'RGBA')
        '''
        self.name = name
        self.mode = mode
        if matteColor:
            self.matteColor = ImageColor.getrgb(matteColor)
        else:
            self.matteColor = (255, 255, 255, 0)
        self.drawBackgrounds = drawBackgrounds
        self.layout = layout
    
    @property
    def transformedImages(self):
        '''
        returns all images which are included in generated SpriteSheet
        with transformed properties
        '''
        for image, rect in self.layout.placedImages:
            image.setOuterPos(rect.topleft)
            image.filename = self.getSpriteSheetFilename()
            yield image

    def getSpriteSheetPath(self):
        return os.path.join(_imageFolder, self.getSpriteSheetFilename())
    
    def getSpriteSheetFilename(self):
        return self.name + '.png'

    def write(self):
        self._placeImages()
        self._writeSpriteSheet()
        self._printInfo()

    def _writeSpriteSheet(self):
        sheet = PIL.Image.new(self.mode, self.layout.size, self.matteColor)
        self._drawImagesInto(sheet)
        self._saveFile(sheet)

    def _placeImages()
        self.layout.placeImages()

    def _drawImagesInto(self, sheet):
        for im, rect in self.layout.placedUniqueImages:
            if not self.drawBackgrounds:
                im.background = None
            im.drawInto(sheet, rect)
        
    def _saveFile(self, sheet):
        path = self.getSpriteSheetPath()
        if _pngOptimizer:
            self_writeOptimizedImage(path)
        else:
            sheet.save(path, optimize=True)

    def _writeOptimizedImage(self, path):
        tmpfile = tempfile.NamedTemporaryFile(suffix='png').name
        sheet.save(tmpfile, 'PNG')
        os.system(_pngOptimizer % (tmpfile, path))
        os.remove(tmpfile)
        
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

