from datetime import datetime

class CssWriter:
    def __init__(self):
        self.selectorToImage = {}
        self.version = datetime.now().strftime('%Y-%m-%dT%H:%M')
        self.fout = None

    def register(self, spriteSheet):
        for image, sheetPos in spriteSheet.transformedImages:
            for p in image.cssProp:
                self.selectorToImage[p.selector] = image, self._transformPos(p.pos, sheetPos)

    def write(self, filename, pathPrefix=''):
        '''
        writes out CSS file
        pathPrefix - path prefix for spritesheets images in css file
        '''
        self.pathPrefix = pathPrefix

        self.fout = file(filename, 'w')
        for selector, value in self.selectorToImage.items():
            image, pos = value            
            self._writeImageCss(selector, image, pos)
        self.fout.close()

    def _writeImageCss(self, selector, image, pos):
        imagePath = self.pathPrefix + image.filename + '?' + self.version
        repeat = image.repeat
        color = image.color or ''
        pos = '%dpx %dpx' % pos
        self.fout.write('%(selector)s {background: %(color)s url(%(imagePath)s) %(repeat)s %(pos)s;}\n' % locals())

    def _transformPos(self, pos, sheetPos):
        sx, sy = sheetPos
        x, y = pos
        return x - sx, y - sy
