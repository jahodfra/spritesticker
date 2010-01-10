'''
auxilliary functions for drawing repeated images
'''

from PIL import Image, ImageColor
from packing import Rect

def draw(sheet, sheetImage, rect):
    if sheetImage.color:
        pasteColor(sheet, sheetImage.color, rect)
    if sheetImage.background:
        draw(sheet, sheetImage.background, rect)

    repeatX, repeatY = sheetImage.getRepeats()
    pos = sheetImage.getInnerPos(rect.topleft)
    blitSurface(sheetImage.image, pos, sheet, rect, repeatX, repeatY)

def pasteColor(sheet, color, rect):
    r, g, b = ImageColor.getrgb(color)
    color = r, g, b, 255
    sheet.paste(color, rect.box)

def _cropSource(src, pos, destRect):
    '''
    crop src rect and destRect to ensure that the source image
    will not over stretch the destination image

    returns cropped source image and cropped destRect
    '''
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
    'auxilliary function handling transparency blitting'
    src, rect = _cropSource(src, pos, destRect)
    if src.mode == 'RGBA':
        dest.paste(src, rect.topleft, src)
    else:
        dest.paste(src, rect.topleft)

def blitSurface(src, pos, dest, destRect, repeatX, repeatY):
    '''
    blit PIL.Image src into PIL.Image dest
    considering src image shifting and repeat

    attributes:
        src - source PIL.Image
        pos - position of source image in the destination image
        dest - destination PIL.Image
        destRect - destination area rect
        repeatX - toggle vertical repeat source image
        repeatY - toggle horizontal repeat source image
    '''

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

