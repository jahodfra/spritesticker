'''
FEATURES
    * multiple used images are placed into spritesheet only oncere
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
    * implement horizontal repeat
    * enable adding images to corners and centers / 3x3 container
    * enable generating markup blocks
    * polish documentation + examples
'''

from sprite import (SpriteSheet,
                    SheetImage,
                    CssWriter,
                    setPngOptimizer,
                    setImageFolder)

from layouts import (SpriteLayout,
                     RepeatXLayout,
                     BoxLayout)
