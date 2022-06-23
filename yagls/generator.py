positive = ["yes", "y", "ok", "okay", "right", "true"]
negative = ["no", "n", "not", "don", "don't", "dont", "do not", "false"]
questions = []


def question(fn):
    questions.append(fn)
    return fn


def generateLabels():
    labels = []
    for i in questions:
        labels += i()

    return labels


@question
def questionPlatform():
    androidPack = [
        {"name": "Platform: Android", "color": "f9d0c4", "description": ""},
        {"name": "Platform: iOS", "color": "25ACBC", "description": ""},
    ]
    desktopPack = [
        {"name": "Platform: Linux", "color": "D711A8", "description": ""},
        {"name": "Platform: macOS", "color": "49A363", "description": ""},
        {"name": "Platform: Windows", "color": "0BFAEC", "description": ""},
    ]
    print("[Platform labels]")
    a = input("This repository much depends on platform? ")
    if a.lower() in positive:
        a = input("Android? or desktop? or both? ")
        if a.lower() == "android":
            return androidPack
        elif a.lower() == "desktop":
            return desktopPack
        elif a.lower() == "both":
            return androidPack + desktopPack
