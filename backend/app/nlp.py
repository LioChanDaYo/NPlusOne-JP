from sudachipy import tokenizer, dictionary
from typing import Set


tok = dictionary.Dictionary().create()
mode = tokenizer.Tokenizer.SplitMode.C


# normalise un peu (kana/kanji formes longues)
def to_lemmas(text: str) -> Set[str]:
    return {m.dictionary_form() for m in tok.tokenize(text, mode)}


# N+1: vrai si exactement 1 lemme inconnu hors particules fréquentes
PARTICLES = {"は","が","を","に","で","と","も","へ","や","の","から","まで","より","か","ね","よ"}


def is_n_plus_1(sentence: str, target: str, known_lemmas: Set[str]) -> bool:
    lemmas = to_lemmas(sentence)
    unknown = [l for l in lemmas if l not in known_lemmas and l not in PARTICLES]
    # permettre que le target soit l'unique inconnu
    if target not in lemmas:
        return False
    return len([u for u in unknown if u != target]) == 0