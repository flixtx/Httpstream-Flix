class StremioStream:
    def __init__(self, url: str, headers: dict | None = None, name: str = "", title: str = "", not_web_ready: bool = False):
        self.name = name
        self.title = title
        self.url = url
        self.not_web_ready = not_web_ready
        if headers is not None:
            self.headers = headers
        else:
            self.headers = {}

    def to_dict(self):
        return {
            "name": self.name,
            "title": self.title,
            "url": self.url,
            "behaviorHints": {
                "notWebReady": self.not_web_ready,
                "proxyHeaders": self.headers,
            },
        }


class StremioStreamManager:
    def __init__(self):
        self.streams: list[StremioStream] = []

    def append(self, stream: StremioStream):
        self.streams.append(stream)

    def to_list(self):
        return [stream.to_dict() for stream in self.streams]

    def to_dict(self):
        return {"streams": self.to_list()}
