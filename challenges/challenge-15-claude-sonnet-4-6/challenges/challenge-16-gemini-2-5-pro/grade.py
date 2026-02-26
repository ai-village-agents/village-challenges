import json
import os

SECRET_PHRASE = "friction-is-frustrating"


def grade():
    score = 0
    message = ""

    if os.path.exists("submission.txt"):
        with open("submission.txt", "r") as f:
            contents = f.read().strip()

        if contents == SECRET_PHRASE:
            score = 100
            message = "Congratulations! You have successfully completed the Broken Tool Challenge."
        else:
            score = 0
            message = "The submission.txt file exists, but it does not contain the correct secret phrase."
    else:
        score = 0
        message = "The submission.txt file was not found."

    results = {
        "score": score,
        "message": message
    }

    with open("results.json", "w") as f:
        json.dump(results, f)


if __name__ == "__main__":
    grade()
