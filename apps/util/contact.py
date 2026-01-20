
from typing import List
import re


def verified_email(email: str) -> bool:
    """
    Vérifie si l'adresse e-mail est valide.
    """
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None