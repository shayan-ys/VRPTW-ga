def pairwise(a: list) -> iter:
    """
    Iterate list items two by two
    Source: https://stackoverflow.com/a/5764948/4744051
    :param a: Given list, e.g.: a = [5, 7, 11, 4, 5]
    :return: Iterable pairs: [5, 7], [7, 11], [11, 4], [4, 5]
    """
    return zip(a[:-1], a[1:])


def couples(iterable):
    """
    Iterate over pairs (even-odd)
    :param iterable: s = s0, s1, s2, s3, s4, s5, ...
    :return: (s0, s1), (s2, s3), (s4, s5), ...
    """
    a = iter(iterable)
    return zip(a, a)
