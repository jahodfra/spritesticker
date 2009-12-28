#!/usr/bin/env python

from spritesticker import *

imageUrlPrefix = 'Images'
imageFolder = r'test/Images'

setPngOptimizer('pngcrush %s %s > /dev/null')
setImageFolder('test/Images')

boxLayout = BoxLayout([
    SheetImage('footer-logo.png') 
        .setSelector('.img-footer-logo') 
        .setBackground(SheetImage('footer-bg.png', pos=(0, -20))),
])

verticalLayout = RepeatXLayout([
    SheetImage('heading-bg.png', pos=(0, 15), margin=(20, 0, 20, 0), color='white', repeat='repeat-x') 
        .setSelector('.img-heading-bg'),
])

noRepeat = SpriteSheet('spritesheet', boxLayout, drawBackgrounds=False, mode='RGB', matteColor='white')
verticals = SpriteSheet('spritesheet-vert', verticalLayout, mode='RGB', matteColor='white')

noRepeat.write()
verticals.write()

cssWriter = CssWriter()
cssWriter.register(noRepeat)
cssWriter.register(verticals)
cssWriter.write(r'test/images.css', pathPrefix='Images/')

