import json
import random
from pathlib import Path
from django.conf import settings

SPECIAL_CHARS = ["_", ".", "-"]

NAMES_FILE = settings.BASE_DIR / "atlas" / "fixtures" / "names.json"

with open(NAMES_FILE, "r", encoding="utf-8") as f:
    WORDS = json.load(f)


def generate_username():
    word1 = random.choice(WORDS)
    word2 = random.choice(WORDS)

    while word1 == word2:
        word2 = random.choice(WORDS)

    username = f"{word1}{word2}"

    if random.random() < 0.7:
        username += random.choice(SPECIAL_CHARS)

    username += str(random.randint(100, 9999))

    return username.lower()
