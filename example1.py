from spriteGen import *

imageUrlPrefix = 'Images'
imageFolder = r'test/Images'

setPngOptimizer('pngcrush %s %s > /dev/null')
setImageFolder('test/Images')

bagLayout = [
    SheetImage('footer-logo.png') 
        .setSelector('.img-footer-logo') 
        .setBackground(SheetImage('footer-bg.png', pos=(0, -20))),
]

verticalLayout = [
    SheetImage('heading-bg.png', pos=(0, 15), margin=(20, 0, 20, 0), color='white', repeat='repeat-x') 
        .setSelector('.img-heading-bg'),
]

noRepeat = SpriteSheet('spritesheet', images=bagLayout, drawBackgrounds=False, mode='RGB', matteColor='white')
verticals = VerticalSheet('spritesheet-vert', images=verticalLayout, mode='RGB', matteColor='white')

noRepeat.write()
verticals.write()

cssWriter = CssWriter()
cssWriter.extend(noRepeat)
cssWriter.extend(verticals)
cssWriter.write(r'test/images.css', pathPrefix='Images/')

