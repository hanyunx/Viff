from field import *

def legendre_mod_p(a, p):
    """Return the legendre symbol ``legendre(a, p)`` where *p* is the
    order of the field of *a*.

    The legendre symbol is -1 if *a* is not a square mod *p*, 0 if
    ``gcd(a, p)`` is not 1, and 1 if *a* is a square mod *p*:

    >>> from viff.field import GF
    >>> legendre_mod_p(GF(5)(2))
    -1
    >>> legendre_mod_p(GF(5)(5))
    0
    >>> legendre_mod_p(GF(5)(4))
    1
    """
    assert p % 2 == 1
    b = (a ** ((p - 1)/2))
    if b == 1:
        return 1
    elif b == p -1:
        return -1
    return 0

p = 0x73eda753299d7d483339d80809a1d80553bda402fffe5bfeffffffff00000001

i = 0
while i < p:
    if legendre_mod_p(i, p) == -1:
        print i, "done!"
        break
    else:
        print i, "pass"

    i += 1