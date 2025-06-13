import asyncio
import typing
import re

from bs4 import BeautifulSoup
import aiohttp

from .exceptions import *


class IMDB:
    def __init__(self, title, year):
        self.title = title
        self.year = year

    def __str__(self):
        return f"<title: {self.title} | year: {self.year}>"

    @classmethod
    async def get(cls, code: str, lang: typing.Literal["en", "fr", "de", "es", "pt", "ja", "zh"] = "en"):
        # list of languages accepted by imdb
        accept_languages = {
            "en": "en-US,en;q=0.9",  # US English
            "fr": "fr-FR,fr;q=0.9",  # French
            "de": "de-DE,de;q=0.9",  # German
            "es": "es-ES,es;q=0.9",  # Spanish (Spain)
            "pt": "pt-BR,pt;q=0.9",  # Brazilian Portuguese
            "ja": "ja-JP,ja;q=0.9",  # Japanese
            "zh": "zh-CN,zh;q=0.9",  # Simplified Chinese
        }

        # get header value for the specified language
        try:
            lang = accept_languages[lang]
        except KeyError:
            msg = f"Invalid value for attribute 'lang'. Got '{lang}', expected any of the following: ['en', 'fr', 'de', 'es', 'pt', 'ja', 'zh']"
            raise AttributeError(msg)

        # get media page
        async with aiohttp.ClientSession() as session:
            imdb_url = f"https://www.imdb.com/title/{code}/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:137.0) Gecko/20100101 Firefox/137.0",
                "Accept-Language": lang,
            }
            async with session.get(imdb_url, headers=headers) as response:
                if response.status != 200:
                    msg = f"Bad status code when requesting IMDb page. Expected '200', got '{response.status_code}'"
                    raise Exception(msg)

                imdb_html = BeautifulSoup(await response.text(), "html.parser")

        # get title
        title = imdb_html.find("h1").text
        if not title:
            msg = "Error while parsing IMDb page. Could not find 'title'."
            raise IMDBParsingError(msg)

        # get release year by finding an 'li' element with exactly 4 integers
        year = 0
        for ul in imdb_html.find_all("ul"):
            ul: BeautifulSoup
            li_elements = ul.find_all("li", {"class": "ipc-inline-list__item"})
            for li in li_elements:
                text = li.text.strip()
                matches = re.match(r"\d{4}", text)
                if matches:
                    year = int(matches[0])
        if not year:
            msg = "Error while parsing IMDb page. Could not find 'year'"
            raise IMDBParsingError(msg)

        return IMDB(title, year)


async def main():
    tasks = [
        IMDB.get("tt1305826"),
        IMDB.get("tt32149847"),
        IMDB.get("tt23649128"),
        IMDB.get("tt31806037"),
        IMDB.get("tt11280740"),
    ]

    results = await asyncio.gather(*tasks)
    for result in results:
        print(result)


if __name__ == "__main__":
    asyncio.run(main())
