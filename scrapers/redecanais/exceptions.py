class VideoPageParsningError(Exception):
    """Failed to extract video url from video page"""


class VideoPlayerParsningError(Exception):
    """Failed to extract videojs url from video player page"""


class ServerFormsParsingError(Exception):
    """Could not extract download page url from serverforms html"""


class DownloadPageParsingError(Exception):
    """Could not extract download page url from serverforms html"""


class EncodedParsingError(Exception):
    """Error parsing the raw list of encoded chars"""


class DecoderError(Exception):
    """Something went wrong when decoding with the given payload and key"""


class UnexpectedStatusCode(Exception):
    """The request returned an unexpected status code"""
