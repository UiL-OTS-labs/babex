
def x_or_else(x, y):
    """If x is not None/empty string, return x. Else, return y.
    (This is not the same as 'x = x or y', as this will also return x when
    'x == False')
    """
    if x is None or x == '':
        return y

    return x