import asyncio
import aiohttp


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
        self.connection = None

    def connect(self):
        self.connection = aiohttp.ClientSession(
            "https://api.github.com",
            headers={"Authorization": "token " + self.token, "User-Agent": "ygl"},
        )

    async def close(self):
        await self.connection.close()

    async def getLabels(self, owner, repo):
        r = await self.connection.get(f"/repos/{owner}/{repo}/labels")
        if r.status == 404:
            raise ResourceNotFound()
        json = await r.json()
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

    async def getLabel(self, owner, repo, name):
        r = await self.connection.get(f"/repos/{owner}/{repo}/labels/{name}")
        if r.status == 404:
            raise ResourceNotFound()
        json = await r.json()
        removeUnneededData(json)
        return json

    async def getBestRepo(self, repo):
        r = await self.connection.get(
            f"/search/repositories?q={repo} in:name&per_page=1"
        )
        if r == 422:
            raise ValidationFailed()
        elif r == 503:
            raise ServiceUnavailable()
        return tuple((await r.json())["items"][0]["full_name"].split("/"))


def removeUnneededData(json):
    del json["id"]
    del json["node_id"]
    del json["url"]
    del json["default"]
