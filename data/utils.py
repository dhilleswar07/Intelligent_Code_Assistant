def clean_text(text):
    """
    Clean and normalize text.
    """

    text = text.strip()

    text = text.lower()

    return text


def count_words(text):
    """
    Count words in a text string.
    """

    words = text.split()

    return len(words)


def reverse_text(text):
    """
    Reverse a string.
    """

    return text[::-1]