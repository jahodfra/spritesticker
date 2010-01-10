#!/usr/bin/env python

from spritesticker import *

imageUrlPrefix = 'Images'
imageFolder = r'test/Images'

setPngOptimizer('pngcrush %s %s > /dev/null')
setImageFolder('test/Images')

noRepeat = SpriteSheet(
    name = 'spritesheet',
    layout = BoxLayout([
        SheetImage(
            image = 'footer-logo.png',
            selector = '.img-footer-logo',
            background = SheetImage(
                image = 'footer-bg-png',
                pos = (0, -20),
            )
        ),
    ])
    drawBackgrounds = False,
    mode = 'RGB',
    matteColor = 'white'
)

verticals = SpriteSheet(
    name = 'spritesheet-vert',
    layout = RepeatXLayout([
        SheetImage(
            image = 'heading-bg.png',
            selector = '.img-heading-bg',
            pos = (0, 15),
            margin = (20, 0, 20, 0),
            color = 'white',
            repeat = 'repeat-x',
        ),
    )]
    mode = 'RGB',
    matteColor = 'white'
)

noRepeat.write()
verticals.write()

cssWriter = CssWriter()
cssWriter.register(noRepeat)
cssWriter.register(verticals)
cssWriter.write(r'test/images.css', pathPrefix='Images/')

