# functions to extract stream links from site sources

from urllib.parse import urlencode, parse_qs, urlparse, urljoin
import re

from bs4 import BeautifulSoup
import aiohttp

from utils.stremio import StremioStream
from .utils import convert_to_punycode
from .decoders import decode_from_text, decode_videojs
from .exceptions import *

REDECANAIS_URL = "https://redecanais.gs/"
# VIDEO_HOST_URL = "https://xn----------------g34l3fkp7msh1cj3acobj33ac2a7a8lufomma7cf2b1sh.xn---1l1--5o4dxb.xn---22--11--33--99--75---------b25zjf3lta6mwf6a47dza94e.xn--pck.xn--zck.xn--0ck.xn--pck.xn--yck.xn-----0b4asja8cbew2b4b0gd0edbjm2jpa1b1e9zva7a0347s4da2797e7qri.xn--1ck2e1b/player3"

HOSTS = [
    urlparse(REDECANAIS_URL).hostname,
]

# TODO FIXME
# class DownloadStream:
#     @classmethod
#     async def get_video_player_url(cls, video_page_url: str) -> str:
#         return await PlayerStream.get_video_player_url(video_page_url)

#     @classmethod
#     async def get_download_page_url(cls, video_player_url: str) -> str:
#         """Get the url of the download page of the given video player url"""
#         async with aiohttp.ClientSession() as session:
#             async with session.get(video_player_url, allow_redirects=False) as redirect:
#                 # idna encode url to work with requests
#                 encoded_url = redirect.headers["location"]
#                 try:
#                     idna_url = convert_to_punycode(f"https:{encoded_url}")
#                 except:
#                     idna_url = encoded_url

#             # parse the decoded html to extract serverforms url and token from the decoded html
#             async with session.get(idna_url) as response:
#                 decoded_html = BeautifulSoup(await decode_from_response(response), "html.parser")

#             scripts = decoded_html.find_all("script")
#             for script in scripts:
#                 url_match = re.findall(r"url: \'\.(/.+?)\'", script.text)
#                 if url_match:
#                     url_match = url_match[0]
#                     serverforms_url = f"{VIDEO_HOST_URL}{url_match}"
#                     rctoken = re.findall(r"\'rctoken\':\'(.+?)\'", script.text)[0]

#             # request the serverforms url
#             async with session.post(serverforms_url, data={"rctoken": rctoken}) as serverforms_response:
#                 # extract download page url from serverforms
#                 download_page_url = re.findall(r"baixar=\"https://.+?r=(.+?)\"", await serverforms_response.text())

#             # return download page url
#             if download_page_url:
#                 return download_page_url[0]
#             else:
#                 msg = "Could not extract download page url from serverforms html"
#                 raise ServerFormsParsingError(msg)

#     @classmethod
#     async def get_download_stream_url(cls, download_page_url: str) -> str:
#         """Extract the download link from the given download page"""
#         # decode download page
#         async with aiohttp.ClientSession() as session:
#             async with session.get(download_page_url) as download_page_response:
#                 download_page = await decode_from_response(download_page_response)

#             # extract download link from download page
#             download_link = re.findall(r"const *redirectUrl *= *\'(.+?)\'", download_page)
#             if download_link:
#                 return f"https:{download_link[0]}"
#             else:
#                 msg = "Could not extract download link from download page"
#                 raise DownloadPageParsingError(msg)

#     @classmethod
#     async def get(cls, video_page_url: str) -> StremioStream:
#         video_player_url = await cls.get_video_player_url(video_page_url)
#         download_page_url = await cls.get_download_page_url(video_player_url)
#         stream = await cls.get_download_stream_url(download_page_url)

#         headers = {
#             "Referer": download_page_url,
#         }

#         return StremioStream(stream, headers=headers)


class PlayerStream:
    @classmethod
    async def get_video_player_url(cls, video_page_url: str) -> str:
        """Extract video player url from a given video page, such as the page for a movie or a specific episode of a series"""
        print("get_video_player_url")
        # get video page
        async with aiohttp.ClientSession() as session:
            async with session.get(video_page_url) as video_page_response:
                decoded_html = decode_from_text(await video_page_response.text(), 1)
                if not (200 <= video_page_response.status <= 299):
                    msg = f"Unexpected status code when requesting video page '{video_page_response.status}'"
                    raise UnexpectedStatusCode(msg)

                video_page_html = BeautifulSoup(decoded_html, "html.parser")

            # get video url
            player_url = ""
            for iframe in video_page_html.find_all("iframe"):
                name = iframe.get("name")
                if name is not None and name == "Player":
                    player_url = iframe.get("src")
                    player_url = urljoin(REDECANAIS_URL, player_url)

            print(player_url)

            if player_url:
                return player_url
            else:
                msg = "Failed to extract video player url from video page"
                raise VideoPageParsningError(msg)

    @classmethod
    async def get_videosjs_url(cls, video_player_url: str) -> str:
        print("get_videojs_url")
        async with aiohttp.ClientSession() as session:
            async with session.get(video_player_url) as video_player_response:
                text = await video_player_response.text()
                decoded_html = decode_from_text(text, 0)
                if not (200 <= video_player_response.status <= 299):
                    msg = f"Unexpected status code when requesting video page '{video_player_response.status}'"
                    raise UnexpectedStatusCode(msg)

                html = BeautifulSoup(decoded_html, "html.parser")

            # extract videojs url from video player html
            scripts = html.find_all("script")
            for script in scripts:
                # find script containing the videojs url
                if "VkFfQlVTQ0FSX0VNX09VVFJPX0xVR0FSX0hF" in script.text:
                    # ignore portion after the url strings
                    text = script.text.split(";")[0]
                    print(text)

                    # ignore + and " chars
                    videojs_url = "".join(re.findall(r"\"([^\+\"]+?)\"", text))
                    videojs_url = urljoin(REDECANAIS_URL, videojs_url)
                    print(videojs_url)

                    return videojs_url

            msg = "Failed to extract videojs url from video player page"
            raise VideoPlayerParsningError(msg)

    @classmethod
    async def get_stream_url(cls, videojs_url: str):
        print("get_stream_url")
        async with aiohttp.ClientSession() as session:
            async with session.get(videojs_url) as videojs_response:
                text = await videojs_response.text()
                decoded_text = decode_videojs(text)

            urls = re.findall(r"(?:\"(?:https?:)?(//.+?)\")", decoded_text)
            urls = ["https:" + url for url in urls]

            for url in urls:
                try:
                    query_params = url.split("?")[1]
                    query_params = parse_qs(query_params)
                except IndexError:
                    continue

                if list(query_params) == ["sv", "nu3zAQc9HC3GbwJq"]:
                    print(url)
                    return url

    @classmethod
    async def get(cls, video_page_url: str):
        print("get")
        video_player_url = await cls.get_video_player_url(video_page_url)
        videojs_url = await cls.get_videosjs_url(video_player_url)
        stream = await cls.get_stream_url(videojs_url)

        # add stream host to list of allowed hosts
        hostname = urlparse(stream).hostname
        if hostname not in HOSTS:
            HOSTS.append(hostname)

        headers = {"Referer": REDECANAIS_URL}

        return StremioStream(stream, headers=headers)


# async def download_stream(video_page_url: str) -> StremioStream:
#     return await DownloadStream.get(video_page_url)


async def player_stream(video_page_url: str) -> StremioStream:
    return await PlayerStream.get(video_page_url)
