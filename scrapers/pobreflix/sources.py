# functions to extract stream links from site sources

import re

import aiohttp
from bs4 import BeautifulSoup

from utils.stremio import StremioStream
from .exceptions import *


class StreamtapeStream:
    @classmethod
    async def get(cls, streamtape_url: str) -> StremioStream:
        async with aiohttp.ClientSession() as session:
            # get video page
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:137.0) Gecko/20100101 Firefox/137.0",
                "Referer": "https://pobreflixtv.love/",
            }
            response = await session.get(streamtape_url, headers=headers)

            # redirect if necessary
            if "window.location.href" in await response.text():
                matches = re.findall(r"window.location.href *= *\"(.+)\" *;?", await response.text())
                redirect_url = matches[0]
                response.release()
                response = await session.get(redirect_url)

            # check status code
            if response.status != 200:
                msg = f"Unexpected status code when getting streamtape url. Expected '200', got '{response.status}'"
                raise UnexpectedStatusCode(msg)

            html = BeautifulSoup(await response.text(), "html.parser")
            response.release()

        # find script element containing the stream link
        stream_url = ""
        for script in html.find_all("script"):
            matches = re.findall(r"document.getElementById\('ideoooolink'\).innerHTML *?= *?\"/*(.+?)\".*?\('(.+?)'\).(.+?);", script.text)
            if matches:
                # get start and end of the stream url
                start = matches[0][0]
                end = matches[0][1]

                # get offset of the end string
                offset_str = matches[0][2]
                offset = 0
                for char in offset_str:
                    char: str
                    if char.isdigit():
                        offset += int(char) + 1

                stream_url = "https://" + start + end[offset - 1 :]

        if stream_url:
            return StremioStream(stream_url)
        else:
            msg = "Error extracting stream url from streamtape"
            raise StreamtapeParsingError(msg)


async def streamtape_stream(streamtape_url: str) -> StremioStream:
    return await StreamtapeStream.get(streamtape_url)
