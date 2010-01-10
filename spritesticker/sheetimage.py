import os
import PIL

from rect import Rect

_imageFolder = ''

def setImageFolder(path):
    '''
    set a path to image folder
    simplifies the path definition for SpriteSheets and SheetImages
    '''
    global _imageFolder
    _imageFolder = path

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

    def __init__(self, filename=None, image=None, margin=(0,0,0,0), pos=(0,0), color=None, background=None, selector='', repeat='no-repeat'):
        '''
        image can be filename or PIL.Image object
        pos - shifting image in pixels from topleft corner of image (not including margin).
              Usefull for dynamicly positioning image in div. Used only for CSS generation
              and background positioning
        image  - PIL.Image.Image instance
        filename - image filename
        margin - top, right, bottom, left margin values
                 it is used for reserving free space around image in sprite sheet.
                 Image size + margin + abs(image position) should be greater than containing div size.
        color, repeat - counterpart of same CSS property
        '''
        if filename and image:
            raise ArgumentError('only filename or image argument can be provided')
        if not filename and not image:
            raise ArgumentError('filename or image argument has to be provided')
            
        self.margin = margin
        if image:
            assert isinstance(image, PIL.Image.Image), 'other image types are not supported'
            self.filename = ''
            self.path = ''
            self.image = image
        elif filename:
            self.filename = filename
            self.path = os.path.join(_imageFolder, self.filename)
            self.image = PIL.Image.open(self.path)

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

    def setOuterPos(self, innerPos):
        innerX, innerY = innerPos        
        self.pos = (self.pos[0] - innerX - self.marginLeft,
                    self.pos[1] - innerY - self.marginTop)

    def getInnerPos(self, outerPos):
        outerX, outerY = outerPos        
        return (outerX + self.pos[0] + self.marginLeft,
                outerY + self.pos[1] + self.marginTop)

    def getOuterRect(self):
        r = Rect()
        r.size = (self.marginLeft + self.image.size[0] + self.marginRight,
                  self.marginTop + self.image.size[1] + self.marginBottom)
        return r

    def getRepeats(self):
        return self._repeatDict[self.repeat]

for i, name in enumerate(('Top', 'Right', 'Bottom', 'Left')):
    pname = 'margin' + name
    getter = lambda self: self.margin[i]
    setattr(SheetImage, pname, property(fget=getter))
