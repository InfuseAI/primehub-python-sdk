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


def display_list(data, width=0, indent=0):
    count = 0
    for x in data:
        if isinstance(x, dict):
            display_tree_like_format(x, width, indent + 2)
            print()
            continue

        if count == 0:
            print("{}- {}".format(" " * (indent - 2), x))
        else:
            print("{}{}".format(" " * indent, x))
        count = count + 1


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
        elif isinstance(v, list):
            print("{}{}:".format(" " * indent, k))
            for x in v:
                if isinstance(x, dict):
                    display_tree_like_format(x, width - 2, indent + 2)
                    continue
                if isinstance(x, list):
                    display_list(x, width - 2, indent + 2)
                    continue
                print("{}{}:{}{}".format(" " * indent, k, " " * remaining, v))
        else:
            print("{}{}:{}{}".format(" " * indent, k, " " * remaining, v))
