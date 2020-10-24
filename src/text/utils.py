from enum import Enum


class TextLevel(str, Enum):
    paragraph = 'paragraph',
    sentence = 'sentence',
    word = 'word'


# Тип метавершины
class TextMVType(str, Enum):
    morph = 'morph'


# Атрибуты метавершины
class MVAttr(str, Enum):
    text = 'text'
    level = 'level'
    token_index = 'token_index',
    mv_type = 'mv_type'
    processed = 'processed',
    lemma = 'lemma',
    pos = 'pos',
    syntax_parsed = 'syntax_parsed'


# Атрибуты метаребра
class MEAttr(str, Enum):
    oriented = 'oriented'


def get_next_level(level: TextLevel) -> TextLevel or None:
    if level == TextLevel.paragraph:
        return TextLevel.sentence

    if level == TextLevel.sentence:
        return TextLevel.word

    if level == TextLevel.word:
        return None


def debug(*args) -> None:
    print(*args)
