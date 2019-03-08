
def x_or_else(x, y):
    """If x is not None/empty string, return x. Else, return y"""
    if x is None or x == '':
        return y

    return x