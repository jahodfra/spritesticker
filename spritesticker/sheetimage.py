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

class CssProp:
    def __init__(self, selector, pos=(0,0)):
        self.selector = selector
        self.pos = pos

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

    def __init__(self, filename=None, image=None, margin=(0,0,0,0), pos=(0,0), color=None, background=None, usedInCss=None, repeat='no-repeat'):
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
            
        if image:
            assert isinstance(image, PIL.Image.Image), 'other image types are not supported'
            self.filename = ''
            self.path = ''
            self.image = image
        elif filename:
            self.filename = filename
            self.path = os.path.join(_imageFolder, self.filename)
            self.image = PIL.Image.open(self.path)            

        self._setCssProp(usedInCss)
        self.margin = margin
        #CSS properties
        self.color = color
        self.background = background
        self.repeat = repeat

    def _setCssProp(self, usedIn):
        if usedIn is None:
            self.cssProp = []
            return
        if isinstance(usedIn, str):
            self.cssProp = [CssProp(usedIn)]
        elif isinstance(usedIn, CssProp):
            self.cssProp = [usedIn]
        else:
            if not hasattr(usedIn, '__iter__'):
                raise ArgumentError('usedIn has invalid type %s, it can be str, CssProp or list of CssProp')
            self.cssProp = list(usedIn)

    def getInnerPos(self, outerPos):
        outerX, outerY = outerPos        
        return (
            outerX + self.marginLeft,
            outerY + self.marginTop
        )

    def getOuterRect(self):
        r = Rect()
        r.size = (
            self.marginLeft + self.image.size[0] + self.marginRight,
            self.marginTop + self.image.size[1] + self.marginBottom
        )
        return r

    def getRepeats(self):
        return self._repeatDict[self.repeat]

    @property
    def marginTop(self): return self.margin[0]

    @property
    def marginRight(self): return self.margin[1]

    @property
    def marginBottom(self): return self.margin[2]

    @property
    def marginLeft(self): return self.margin[3]

