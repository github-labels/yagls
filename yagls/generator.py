positive = ["yes", "y", "ok", "okay", "right", "true"]
negative = ["no", "n", "not", "don", "don't", "dont", "do not", "false"]
questions = []


def question(fn):
    questions.append(fn)
    return fn


async def generateLabels(c):
    labels = []
    for i in questions:
        labels += await i(c)

    return labels


@question
async def questionCommon(connection):
    labels = await connection.getLabels("github-labels", "common-label-template")
    print("[Common labels]")
    a = input("Do you want to use common labels? ")
    if a.lower() in positive:
        return labels


@question
async def questionPlatform(connection):
    labels = await connection.getLabels("github-labels", "platform-label-template")
    androidPack = labels[:2]
    desktopPack = labels[2:]
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
