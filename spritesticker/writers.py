class CssWriter:
    def __init__(self):
        self.selectorToImage = {}

    def register(self, spriteSheet):
        for image in spriteSheet.transformedImages:
            if image.selector:
                self.selectorToImage[image.selector] = image

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
