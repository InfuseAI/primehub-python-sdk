import re
import random


def auto_gen_id(name: str):
    normalized_name = re.sub(r'[\W_]', '-', name).lower()
    random_string = str(float.hex(random.random()))[4:9]
    return f'{normalized_name}-{random_string}'
