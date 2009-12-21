from PIL import Image
from packing import Rect

def _cropSource(src, pos, destRect):
    rect = Rect()
    rect.size = src.size

    leftDiff = destRect.left - pos[0]
    if leftDiff > 0:
        rect.width -= leftDiff
        rect.left = leftDiff

    topDiff  = destRect.top  - pos[1]
    if topDiff > 0:
        rect.height -= topDiff
        rect.top = topDiff

    rect.size = (min(rect.size[0], destRect.right  - pos[0] - rect.left),
                 min(rect.size[1], destRect.bottom - pos[1] - rect.top))

    if rect.size != src.size:
        src = src.crop(rect.box)
    rect.topleft = (rect.left + pos[0], rect.top + pos[1])
    return src, rect

def _blitSurface(src, pos, dest, destRect):
    src, rect = _cropSource(src, pos, destRect)
    if src.mode == 'RGBA':
        #bg = dest.crop(rect.box)
        #src = Image.composite(src, bg, src).convert('RGB')
        dest.paste(src, rect.topleft, src)
    else:
        dest.paste(src, rect.topleft)

def blitSurface(src, pos, dest, destRect, repeatX, repeatY):
    left, top = pos
    xCount, yCount = 1, 1
    srcWidth, srcHeight = src.size

    if repeatX:
        left = (pos[0] - destRect.left) % srcWidth + destRect.left
        if left > destRect.left:
            left -= srcWidth
        xCount = destRect.width / srcWidth + 1

    if repeatY:
        top = (pos[1] - destRect.top) % srcHeight + destRect.right
        if top > destRect.top:
            top -= srcHeight
        yCount = destRect.height / srcHeight + 1

    for y in xrange(yCount):
        for x in xrange(xCount):
            _blitSurface(src, (left, top), dest, destRect)
            left += srcWidth
        top += srcHeight

