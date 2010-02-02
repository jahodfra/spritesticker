'''
SpriteSticker
- build tool for web spritesheets

LICENSE (MIT):

Copyright (c) 2009 Frantisek Jahoda

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

FEATURES
    * generates CSS multiple used images are placed into spritesheet only once
    * tries to pack images to smallest rectangle (only estimation) program
    * handles images with repeat-x or repeat-y images can have image background
    * optional optimalization for IE6 (transparency issues) on the fly
    * generated PIL.Images can be added into spritesheet integrated PNG
    * optimizer special referencing of files in css ensure that browser will
      reload them

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
    * polish documentation + examples
    * design and create html page

EXAMPLE:
    see tests/

'''

from spritesheet import (
        SpriteSheet,
        setPngOptimizer)
from layouts import (
        SpriteLayout,
        RepeatXLayout,
        BoxLayout)
from sheetimage import (
        SheetImage,
        CssProp,
        setImageFolder)
from writers import (
        CssWriter)
        
