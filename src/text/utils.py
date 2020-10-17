from enum import Enum


class TextLevel(str, Enum):
    paragraph = 'paragraph',
    sentence = 'sentence',
    word = 'word'


def get_next_level(level: TextLevel) -> TextLevel or None:
    if level == TextLevel.paragraph:
        return TextLevel.sentence

    if level == TextLevel.sentence:
        return TextLevel.word

    if level == TextLevel.word:
        return None


def debug(*args) -> None:
    print(*args)
