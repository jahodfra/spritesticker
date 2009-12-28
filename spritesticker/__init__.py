'''
SpriteSticker
build tool for web spritesheets

- speed up your web
- automatically:
    create web graphic spritesheets
    generate css styles for the sprites
- automatize IE6 PNG transparency issues

FEATURES
    * multiple used images are placed into spritesheet only once
    * tries to pack images to smallest rectangle (only estimation)
    * program handles images with repeat-x or repeat-y
    * images can have image background
    * optional optimalization for IE6 (transparency issues)
    * on the fly generated PIL.Images can be added into spritesheet
    * integrated PNG optimizer

TODO:
    * testy
        * test repeat images
            * image generation
            * css generation
            * no images added
            * bad image type added
        * test no-repat images
            * image generation
            * css generation
            * no images added
            * bad image type added
        * testPacking (not overlapping, preserving size)
    * enable adding images to corners and centers / 3x3 container
    * enable generating markup blocks
    * polish documentation + examples
    * design and create html page

EXAMPLE:
    see tests/
'''

from sprite import (SpriteSheet,
                    SheetImage,
                    CssWriter,
                    setPngOptimizer,
                    setImageFolder)

from layouts import (SpriteLayout,
                     RepeatXLayout,
                     BoxLayout)
