#!/usr/bin/env python

from spritesticker import *

setPngOptimizer('pngcrush %s %s > /dev/null')
setImageFolder('tests/Images')

noRepeat = SpriteSheet(
    name = 'spritesheet',
    layout = BoxLayout([
        SheetImage(
            filename = 'footer-logo.png',
            selector = '.img-footer-logo',
            background = SheetImage(
                filename = 'footer-bg.png',
                pos = (0, -20),
            )
        ),
    ]),
    drawBackgrounds = False,
    mode = 'RGB',
    matteColor = 'white'
)

verticals = SpriteSheet(
    name = 'spritesheet-vert',
    layout = RepeatXLayout([
        SheetImage(
            filename = 'heading-bg.png',
            selector = '.img-heading-bg',
            pos = (0, 15),
            margin = (20, 0, 20, 0),
            color = 'white',
            repeat = 'repeat-x',
        ),
    ]),
    mode = 'RGB',
    matteColor = 'white'
)

noRepeat.write()
verticals.write()

cssWriter = CssWriter()
cssWriter.register(noRepeat)
cssWriter.register(verticals)
cssWriter.write(r'tests/images.css', pathPrefix='Images/')

