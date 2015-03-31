"""Utilities / helpers"""
# -coding=utf-8


def verhoeff_digit(no):
    """
    Implemention of Verhoeff's Dihedral Check Digit

    :param no:
    Source:
    https://github.com/hudora/huTools/blob/master/huTools/checksumming.py
    """

    # dihedral addition matrix A + B = a[A][B]
    _amatrix = ((0, 1, 2, 3, 4, 5, 6, 7, 8, 9),
                (1, 2, 3, 4, 0, 6, 7, 8, 9, 5),
                (2, 3, 4, 0, 1, 7, 8, 9, 5, 6),
                (3, 4, 0, 1, 2, 8, 9, 5, 6, 7),
                (4, 0, 1, 2, 3, 9, 5, 6, 7, 8),
                (5, 9, 8, 7, 6, 0, 4, 3, 2, 1),
                (6, 5, 9, 8, 7, 1, 0, 4, 3, 2),
                (7, 6, 5, 9, 8, 2, 1, 0, 4, 3),
                (8, 7, 6, 5, 9, 3, 2, 1, 0, 4),
                (9, 8, 7, 6, 5, 4, 3, 2, 1, 0))

    # dihedral inverse map, A + inverse[A] = 0
    _inverse = (0, 4, 3, 2, 1, 5, 6, 7, 8, 9)
    # permutation weighting matrix P[position][value]
    _pmatrix = ((0, 1, 2, 3, 4, 5, 6, 7, 8, 9),
                (1, 5, 7, 6, 2, 8, 3, 0, 9, 4),
                (5, 8, 0, 3, 7, 9, 6, 1, 4, 2),
                (8, 9, 1, 6, 0, 4, 3, 5, 2, 7),
                (9, 4, 5, 3, 1, 2, 6, 8, 7, 0),
                (4, 2, 8, 6, 5, 7, 3, 9, 0, 1),
                (2, 7, 9, 3, 8, 0, 6, 4, 1, 5),
                (7, 0, 4, 6, 9, 1, 3, 2, 5, 8))

    check = 0  # initialize check at 0
    i = 0
    for digit in reversed(no):
        digit = ord(digit) - 48
        check = _amatrix[check][_pmatrix[(i + 1) % 8][digit]]
        i += 1
    return chr(_inverse[check] + 48)
