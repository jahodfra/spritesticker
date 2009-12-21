
def gcd(x, y):
    while True:
        if y > x:
            y, x = x, y
        d, r = x / y, x % y
        if r == 0:
            return y
        x, y = d, r

def lcm(x, y):
    d = gcd(x, y)
    return (x / d) * y

def prettySize(size):
    'from http://snippets.dzone.com/posts/show/5434'
    suffixes = [("B",2**10), ("K",2**20), ("M",2**30), ("G",2**40), ("T",2**50)]
    for suf, lim in suffixes:
        if size > lim:
            continue
        else:
            return round(size/float(lim/2**10),2).__str__()+suf

def transpose(pair):
    x, y = pair
    return y, x

def findfirst(filter, iterable):
    for item in iterable:
        if filter(item):
            return item
    return None

