SpriteSticker is a python package which automates CSS sprite sheets generation. It includes multiple images into one image (spritesheet) to shorten web page rendering time and to reduce number of HTTP requests. See https://css-tricks.com/css-sprites/

Features
==
* tries to pack images to smallest rectangle (estimation)
* vertical (repeat-x) sprite sheets
* horizontal (repeat-y) sprite sheets
* sprite can have own image background (for IE 6.0)
* output PNG files can be compressed trough external program e.g [pngcrush](http://pmt.sourceforge.net/pngcrush/)
* multiple used images are placed into spritesheet only once 

Example
==
```python
#!/usr/bin/env python

from spritesticker import *

setImageFolder('test/Images')

noRepeat = SpriteSheet('spritesheet', BoxLayout([
    SheetImage(
      filename = 'blue.png',
      selector =  '.img-blue',
    ),
    SheetImage(
      filename = 'yellow.png',
      selector =  '.img-yellow',
    ),
    SheetImage(
      filename = 'red.png',
      selector =  '.img-red',
      color = 'red',
    ),
]))

noRepeat.write()

cssWriter = CssWriter()
cssWriter.register(noRepeat)
cssWriter.write(r'test/images.css', pathPrefix='Images/')
```

Dependencies
==
```
Python >= 2.5
PIL 
```

Installation
==
install by running `./setup.py install`
