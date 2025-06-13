from urllib.parse import urlencode
import asyncio

from utils.stremio import StremioStream, StremioStreamManager
from .main import get_movie_audios, get_series_audios
from .sources import warezcdn_stream

HOSTS = [
    "basseqwevewcewcewecwcw.xyz",
]


async def movie_streams(imdb: str, proxy_url: str | None = None):
    try:
        audio_list = await get_movie_audios(imdb)
        tasks = []
        for audio in audio_list:
            for server in audio["servers"].split(","):
                if server == "mixdrop":
                    continue
                if server == "warezcdn":
                    tasks.append(warezcdn_stream(imdb, "filme", audio))

        stream_info_list: list[StremioStream] = await asyncio.gather(*tasks)

        streams = StremioStreamManager()
        if proxy_url is None:
            for stream in stream_info_list:
                streams.append(stream)
        else:
            for stream in stream_info_list:
                query = urlencode({"url": stream.url, "headers": stream.headers})
                stream = StremioStream(f"{proxy_url}?{query}", name=stream.name, title=stream.title)
                streams.append(stream)

        return streams.to_list()

    except Exception as e:
        print(f"Exception raised in warezcdn scraper! {e.__class__.__name__}: {e}")
        return []


async def series_stream(imdb: str, season: int, episode: int, proxy_url: str | None = None):
    try:
        audio_list = await get_series_audios(imdb, season, episode)
        tasks = []
        for audio in audio_list:
            for server in audio["servers"].split(","):
                if server == "mixdrop":
                    continue
                if server == "warezcdn":
                    tasks.append(warezcdn_stream(imdb, "filme", audio))

        stream_info_list: list[StremioStream] = await asyncio.gather(*tasks)

        streams = StremioStreamManager()
        if proxy_url is None:
            for stream in stream_info_list:
                streams.append(stream)
        else:
            for stream in stream_info_list:
                query = urlencode({"url": stream.url, "headers": stream.headers})
                stream = StremioStream(f"{proxy_url}?{query}", name=stream.name, title=stream.title)
                streams.append(stream)

        return streams.to_list()

    except Exception as e:
        print(f"Exception raised in warezcdn scraper! {e.__class__.__name__}: {e}")
        return []
