from .yagls import *
import asyncio
import argparse
from pathlib import Path


def parse():
    parser = argparse.ArgumentParser(
        prog="yagls", description="Yet Another github label synchroniser"
    )
    parser.add_argument(
        "FROM", help="Repository to be exported"
    )
    parser.add_argument("TO", nargs='*', help="Repositories to be imported. If TO is not provided, FROM will be TO repository.")
    parser.add_argument(
        "-c", "--clear", action="store_true", help="From repository is be cleared?"
    )
    parser.add_argument(
        "--token",
        default=None,
        help="Github personal access token that repo scope is allowed",
    )
    parser.add_argument("--save", action="store_true", help="Remember token")
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


def parseRepo(s):
    t = s.split("/")
    if len(t) == 1:
        return (None, t[0])
    else:
        return tuple(t)

def parseRepos(d):
    return (parseRepo(i) for i in d)



async def main():
    ns = parse()
    token = tokenLoad()
    if not token and not ns.token:
        print("Token is not provided! Please use --token argument!")
        exit(-1)
    if ns.token:
        token = ns.token
    if ns.save:
        try:
            tokenSave(token)
        except Exception as e:
            print(e)
            print("Failed to save token!")

    c = Connection(token)
    c.connect()

    
    repo = parseRepo(ns.FROM)
    if len(ns.TO)!=0:
        if repo[0] == None:
            try:
                repo = await c.getBestRepo(repo[1])
            except Exception as e:
                print(f"Failed to get repository through name {repo[1]}.")
                await c.close()
                raise
            print(f"Found: {repo[0]}/{repo[1]}")
        try:
            labels = await c.getLabels(*repo)
        except Exception as e:
            print(f"Failed to get labels of {repo[0]}/{repo[1]}")
            await c.close()
            raise
        repos = parseRepos(ns.TO)
    else:
        repos = [repo]
        labels = None

    for repo in repos:
        if repo[0] == None:
            try:
                repo = await c.getBestRepo(repo[1])
            except Exception as e:
                print(f"Failed to get repository through name {repo[1]}.")
                await c.close()
                raise
            print(f"Found: {repo[0]}/{repo[1]}")
        if ns.clear:
            try:
                await c.deleteLabels(*repo)
            except Exception as e:
                print(f"Failed to delete labels of {repo[0]}/{repo[1]}.")
                await c.close()
                raise
        already_exist_flag = False

        if labels:
            try:
                await c.createLabels(*repo, labels)
            except ValidationFailed as e:
                already_exist_flag = True
            except Exception as e:
                print(f"Failed to create labels at {repo[0]}/{repo[1]}.")
                await c.close()
                raise
        if already_exist_flag:
            print(
                f"[{repo[0]}/{repo[1]}] Failed some tries to create label.\n[{repo[0]}/{repo[1]}] Maybe there's already a label with the same name."
            )
    await c.close()
    exit(0)


if __name__ == "__main__":
    asyncio.run(main())
