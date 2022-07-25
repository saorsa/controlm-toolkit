import random
import string


def generate_random_string(
        str_size: int,
        allowed_chars: str = string.ascii_letters + string.punctuation + string.octdigits) -> str:
    return ''.join(random.choice(allowed_chars) for _ in range(str_size))
