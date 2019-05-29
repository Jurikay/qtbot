import random

def startup_sentence():
    """Return a random sentence to display together with the splash screen."""
    sentences = [
        "Booting up",
        "Kiss my shiny metal ass",
        "Calculating gainz",
        "Picking Lambo",
        "Burning excessive money",
        "Running simulations",
        "Calling the Bogdanoffs",
        "BIIICOOONNEEEEEEC",
        "Boy, Sminem, Cool",
        "Funds are safu",
        "B O G G E D",
        "Was is bloß mit IOTA los",
        "In for the technology",
        "Buy high sell low",
        "Whale sounds intensify",
        "🚀🚀🚀"
    ]
    rand = random.randint(0, len(sentences)-1)
    return sentences[rand]



