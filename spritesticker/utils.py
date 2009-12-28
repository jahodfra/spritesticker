'''
usefull functions of all possible kinds
'''

def gcd(x, y):
    '''computes greatest common divisor
    >>> gcd(12, 10)
    2
    >>> gcd(60, 120)
    60
    >>> gcd(29, 13)
    1
    '''
    while True:
        if y > x:
            y, x = x, y
        if y == 0:
            return x
        x, y = y, x % y

def lcm(x, y):
    '''computes the least common multiplier
    >>> lcm(12, 10)
    60
    >>> lcm(5, 10)
    10
    >>> lcm(7, 3)
    21
    >>> lcm(120, 120)
    120
    '''
    d = gcd(x, y)
    return (x / d) * y

def prettySize(size):
    '''
    prints out pretty formated data size
    from http://snippets.dzone.com/posts/show/5434

    >>> prettySize(512)
    '512.0B'
    >>> prettySize(1055)
    '1.03K'
    >>> prettySize(1555666)
    '1.48M'
    '''
    suffixes = [("B",2**10), ("K",2**20), ("M",2**30), ("G",2**40), ("T",2**50)]
    for suf, lim in suffixes:
        if size > lim:
            continue
        else:
            return round(size/float(lim/2**10),2).__str__()+suf

def transpose(pair):
    x, y = pair
    return y, x

def findfirst(cond, iterable):
    '''
    find first item in iterable which satisfies cond

    >>> #first quadratic non-residue of 90
    >>> findfirst(lambda x: (x * x) % 90 == 0, xrange(1, 90))
    30
    '''
    for item in iterable:
        if cond(item):
            return item
    return None

if __name__ == "__main__":
    import doctest
    doctest.testmod()

