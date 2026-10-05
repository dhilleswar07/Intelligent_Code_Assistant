def calculate_average(numbers):
    """
    Calculate the average of a list of numbers.
    """

    if not numbers:
        return 0

    return sum(numbers) / len(numbers)


def find_maximum(numbers):
    """
    Find the maximum number.
    """

    if not numbers:
        return None

    return max(numbers)


def filter_positive_numbers(numbers):
    """
    Return only positive numbers.
    """

    return [
        number
        for number in numbers
        if number > 0
    ]