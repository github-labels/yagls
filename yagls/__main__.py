from .yagls import *
import asyncio
import argparse
from pathlib import Path


def parse():
    parser = argparse.ArgumentParser(
        prog="yagls", description="Yet Another github label synchroniser"
    )
    parser.add_argument("FROM", help="Repository to be exported")
    parser.add_argument("TO", help="Repository to be imported")
    parser.add_argument(
        "-o", "--overWrite", action="store_true", help="From repository is be cleared?"
    )
    parser.add_argument(
        "-f", "--fromOwner", default=None, help="Explict owner of From repository"
    )
    parser.add_argument(
        "-t", "--toOwner", default=None, help="Explict owner of To repository"
    )
    parser.add_argument(
        "--token",
        default=None,
        help="Github personal access token that repo scope is allowed",
    )
    parser.add_argument("--saveToken", action="store_true", help="Remember token")
    ns = parser.parse_args()
    return ns


def tokenLoad():
    try:
        d = Path.home().joinpath(".yagls")
        with open(d.joinpath("token.txt"), "r") as fp:
            return fp.read()
    except Exception:
        return None


def tokenSave(token):
    d = Path.home().joinpath(".yagls")
    d.mkdir(exist_ok=True)
    with open(d.joinpath("token.txt"), "w") as fp:
        fp.write(token)


async def main():
    ns = parse()
    token = tokenLoad()
    if not token and not ns.token:
        print("Token is not provided! Please use --token argument!")
        exit(-1)
    if ns.token:
        token = ns.token
    if ns.saveToken:
        try:
            tokenSave(token)
        except Exception as e:
            print(e)
            print("Failed to save token!")

    c = Connection(token)
    c.connect()
    try:
        if ns.fromOwner:
            repo = (ns.fromOwner, ns.FROM)
            labels = await c.getLabels(*repo)
        else:
            repo = await c.getBestRepo(ns.FROM)
            print(f"Found: {repo[0]}/{repo[1]}")
            labels = await c.getLabels(*repo)
    except Exception:
        print(f"Failed to get labels of {repo[0]}/{repo[1]}")
        await c.close()
        exit(-1)
    if ns.toOwner:
        repo = (ns.toOwner, ns.TO)
    else:
        repo = await c.getBestRepo(ns.TO)
        print(f"Found: {repo[0]}/{repo[1]}")
    try:
        if ns.overWrite:
            await c.deleteLabels(*repo)
        await c.createLabels(*repo, labels)
    except Exception:
        print(f"Failed to import to {repo[0]}/{repo[1]}.")
        await c.close()
        exit(-1)
    await c.close()


if __name__ == "__main__":
    asyncio.run(main())
