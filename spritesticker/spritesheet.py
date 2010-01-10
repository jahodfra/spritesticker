'''
base module
'''

import os
import tempfile

import PIL
from PIL import ImageColor

import sheetimage
from utils import prettySize
from draw import draw

_pngOptimizer = ''

def setPngOptimizer(cmd):
    '''
    set a png optimizer command
    which is called on generated spritesheets

    e.g. pngcrush, pngnq, pngquant can be used
    setPngOptimizer('pngcrush %s %s')
    '''
    global _pngOptimizer
    _pngOptimizer = cmd

class SpriteSheet:
    def __init__(self, name, layout, matteColor=None, drawBackgrounds=True, mode='RGBA'):
        '''
        name - filename without suffix
        matteColor - bakckground color for generated stylesheet
        drawBackgrounds - toggle background images drawing
        mode - is a PIL.Image.mode for generated image ('RGB' or 'RGBA')
        '''
        assert layout, 'must be defined'
        assert name, 'non empty string is needed'

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
            image.filename = self.getFilename()
            yield image

    def getPath(self):
        return os.path.join(sheetimage._imageFolder, self.getFilename())
    
    def getFilename(self):
        return self.name + '.png'

    def write(self):
        self._placeImages()
        self._write()
        self._printInfo()

    def _write(self):
        sheet = PIL.Image.new(self.mode, self.layout.size, self.matteColor)
        self._drawImagesInto(sheet)
        self._saveFile(sheet)

    def _placeImages(self):
        self.layout.placeImages()

    def _drawImagesInto(self, sheet):
        for im, rect in self.layout.placedUniqueImages:
            if not self.drawBackgrounds:
                im.background = None
            draw(sheet, im, rect)
        
    def _saveFile(self, sheet):
        path = self.getPath()
        if _pngOptimizer:
            self._writeOptimizedImage(sheet, path)
        else:
            sheet.save(path, optimize=True)

    def _writeOptimizedImage(self, sheet, path):
        tmpfile = tempfile.NamedTemporaryFile(suffix='png').name
        sheet.save(tmpfile, 'PNG')
        os.system(_pngOptimizer % (tmpfile, path))
        os.remove(tmpfile)
        
    def _printInfo(self):
        self._printBaseInfo()
        self._printSizeInfo()

    def _printBaseInfo(self):
        nImages = self.layout.uniqueImagesCount
        print 'generating %s containing %d images' % (self.getFilename(), nImages)
        print '  dimension %d x %dpx' % self.layout.size
        print '  requests saved %d' % (nImages - 1)
        print '  filling coeficient is %.2f%%' % (self.layout.fillCoef * 100.0)
    
    def _printSizeInfo(self):
        placedImages = list(self.layout.placedUniqueImages)
        newsize = os.path.getsize(self.getPath())
        if all(image.path != '' for image, rect in placedImages):
            origsize = sum(os.path.getsize(image.path) for image, rect in placedImages)
            sizeCoef = float(newsize) / origsize * 100.0
            print '  original images filesize: %s' % prettySize(origsize)
            print '  spritesheet filesize: %s (%.2f%%)' % (prettySize(newsize), sizeCoef)
        else:
            print '  spritesheet filesize: %s' % prettySize(newsize)

