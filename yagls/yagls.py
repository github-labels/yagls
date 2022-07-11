import asyncio
import aiohttp
from .generator import generateLabels


class ResourceNotFound(Exception):
    pass


class ValidationFailed(Exception):
    pass


class ServiceUnavailable(Exception):
    pass


class UnvalidResponseCode(Exception):
    pass


class Connection:
    def __init__(self, token):
        self.token = token
        self.connection = aiohttp.ClientSession(
            "https://api.github.com",
            headers={"Authorization": "token " + self.token, "User-Agent": "yagls"},
        )

    async def close(self):
        await self.connection.close()

    async def getRawLabels(self, owner, repo):
        r = await self.connection.get(f"/repos/{owner}/{repo}/labels")
        if r.status == 404:
            raise ResourceNotFound()
        json = await r.json()
        return json

    async def getLabels(self, owner, repo):
        json = await self.getRawLabels(owner, repo)
        for i in json:
            removeUnneededData(i)
        return json

    async def deleteLabel(self, owner, repo, name):
        r = await self.connection.delete(f"/repos/{owner}/{repo}/labels/{name}")
        if r.status == 404:
            raise ResourceNotFound()

    async def deleteLabels(self, owner, repo):
        r = await self.getLabels(owner, repo)
        await asyncio.gather(*[self.deleteLabel(owner, repo, i["name"]) for i in r])

    async def createLabel(self, owner, repo, label):
        r = await self.connection.post(f"/repos/{owner}/{repo}/labels", json=label)
        if r.status == 404:
            raise ResourceNotFound()
        elif r.status == 422:
            raise ValidationFailed()
        elif r.status != 201:
            raise UnvalidResponseCode(r.status)

    async def createLabels(self, owner, repo, labels):
        await asyncio.gather(*[self.createLabel(owner, repo, i) for i in labels])

    async def getRawLabel(self, owner, repo, name):
        r = await self.connection.get(f"/repos/{owner}/{repo}/labels/{name}")
        if r.status == 404:
            raise ResourceNotFound()
        return await r.json()

    async def getLabel(self, owner, repo, name):
        json = await self.getRawLabel(owner, repo, name)
        removeUnneededData(json)
        return json

    async def getBestRepo(self, repo):
        r = await self.connection.get(
            f"/search/repositories?q={repo} in:name&per_page=1"
        )
        if r.status == 422:
            raise ValidationFailed()
        elif r.status == 503:
            raise ServiceUnavailable()
        return tuple((await r.json())["items"][0]["full_name"].split("/"))

    async def getBestRepos(self, name, n=3):
        r = await self.connection.get(
            f"/search/repositories?q={name} in:name&per_page=3"
        )
        if r.status == 422:
            raise ValidationFailed()
        elif r.status == 503:
            raise ServiceUnavailable()
        l = (await r.json())["items"]
        return tuple(tuple(l[i]["full_name"].split("/")) for i in range(len(l)))

    async def generateLabels(self):
        return await generateLabels(self)


def removeUnneededData(json):
    del json["id"]
    del json["node_id"]
    del json["url"]
    del json["default"]
