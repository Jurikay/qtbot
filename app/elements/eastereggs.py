import random

def startup_sentence():
    """Return a random sentence to display together with the splash screen."""
    sentences = [
        "Booting up",
        "Kiss my shiny metal ass",
        "Calculating gainz",
        "Ordering Lambo",
        "beep boop",
        "Throwing away money",
        "Running simulations",
        "Calling the Bogdanoff's",
        "BIIICOOONNEEEEEEC",
        "Boy, Sminem, Cool",
        "Funds are safu",
        " B O G G E D",
        ""

    ]

    sentence_count = len(sentences)

    rand = random.randint(1, sentence_count)

    return sentences[rand-1]



