from rapidfuzz import process


def match_customer(name, customers):

    best = process.extractOne(name, customers)

    if best and best[1] > 80:
        return best[0]

    return None