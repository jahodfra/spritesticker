from spriteGen import *
from PIL import Image as pilImage

imageUrlPrefix = 'Images'
imageFolder = r'test/Images'

setPngOptimizer('pngcrush %s %s > /dev/null')

noRepeat = SpriteSheet('spritesheet', imageFolder, {
    '.img-footer-logo':
        Image('footer-logo.png',
            background=Image('footer-bg.png', pos=(0, -20), repeat='repeat-x')),

}, drawBackgrounds=False, mode='RGB', matteColor='white')

verticals = VerticalSheet('spritesheet-vert', imageFolder, {
    '.img-heading-bg':
        Image('heading-bg.png', pos=(0, 15), margin=(20, 0, 20, 0), color='white'),

}, mode='RGB', matteColor='white')

noRepeat.write()
verticals.write()

cssFile = CssFile(r'test/images.css', pathPrefix='Images/')
cssFile.extend(noRepeat)
cssFile.extend(verticals)
cssFile.write()

