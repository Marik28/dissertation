import aenum


class Type(aenum.MultiValueEnum):
    """\
    Типы данных, представляемые в протоколе ОВЕН.
    За основу взяты C-типы (https://docs.python.org/3/library/struct.html#format-characters)
    и типы, описанные в документации протокола ОВЕН
    """
    # CHAR = ...
    SIGNED_CHAR = "signed char"
    UNSIGNED_CHAR = ("T", "UB")
    # BOOL = ...
    SHORT = "short"
    UNSIGNED_SHORT = ("I", "unsigned short")
    # INT = ...
    # UNSIGNED_INT = ...
    # LONG = ...
    # UNSIGNED_LONG = ...
    # LONG_LONG = ...
    # UNSIGNED_LONG_LONG = ...
    FLOAT24 = "F24"
    FLOAT = ("F32", "float", "float32")
    STRING = "ASCII"
    NERR = "N.err"