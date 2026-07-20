import random
import string
from django.contrib.auth import get_user_model

User = get_user_model()


def generate_temporary_password(length: int = 12) -> str:
    if length < 4:
        length = 4
    password = [
        random.choice(string.ascii_uppercase),
        random.choice(string.ascii_lowercase),
        random.choice(string.digits),
        random.choice(string.punctuation),
    ]
    all_chars = string.ascii_letters + string.digits + string.punctuation
    password += [random.choice(all_chars) for _ in range(length - 4)]
    random.shuffle(password)
    return "".join(password)


def reset_user_password(user, save: bool = True) -> str:
    new_password = generate_temporary_password()
    user.set_password(new_password)
    user.requires_password_change = True
    if save:
        user.save(update_fields=["password", "requires_password_change"])
    return new_password
