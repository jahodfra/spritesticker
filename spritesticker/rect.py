
class Rect(object):
    '''
    reperesents rectangle object
    and handles settings and recalculating different properties

    >>> r = Rect()
    >>> r.topleft = 1, 5
    >>> r.size = 2, 3
    >>> r.box
    (1, 5, 3, 8)
    >>> r.left
    1
    >>> r.right
    3
    >>> r.height
    3
    '''

    __slots__ = ['left', 'top', 'width', 'height']

    def __init__(self):
        self.left = 0
        self.top = 0
        self.width = 0
        self.height = 0

    def transpose(self):
        'transpose all coordinates'
        self.left, self.top = self.top, self.left
        self.width, self.height = self.height, self.width

    def __str__(self):
        return 'Rect(%d, %d, %d, %d)' % (self.left, self.top, self.width, self.height)

    @property
    def area(self):
        return self.width * self.height
    
    def _get_size(self):
        return self.width, self.height
    def _set_size(self, val):
        self.width, self.height = val

    size = property(_get_size, _set_size)

    def _get_topleft(self):
        return self.left, self.top
    def _set_topleft(self, val):
        self.left, self.top = val

    topleft = property(_get_topleft, _set_topleft)

    @property
    def right(self): return self.left + self.width

    @property
    def bottom(self): return self.top + self.height

    @property
    def bottomright(self): return self.left + self.width, self.top + self.height

    @property
    def box(self): return self.topleft + self.bottomright

if __name__ == "__main__":
    import doctest
    doctest.testmod()

