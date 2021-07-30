import re


def to_upper_words(column_name):
    """
    Convert a column_name to upper words.

    For example: instanceType => INSTANCE TYPE
    """
    tokens = re.split(r'([A-Z]+)', column_name)
    output = []
    while tokens:
        current = tokens.pop(0)
        if current.islower():
            output.append(current)
            continue
        output.append(current + tokens.pop(0))
    return " ".join([x.upper() for x in output])


def display_tree_like_format(data, width=0, indent=0):
    output = [(to_upper_words(k), v) for (k, v) in data.items()]
    if width == 0:
        width = 10 + max([len(x[0]) for x in output])
        if width < 25:
            width = 25

    for k, v in output:
        remaining = width - len(k)
        if isinstance(v, dict):
            print("{}{}:".format(" " * indent, k))
            display_tree_like_format(v, width - 2, indent + 2)
        else:
            print("{}{}:{}{}".format(" " * indent, k, " " * remaining, v))
