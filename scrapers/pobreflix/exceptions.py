class UnexpectedStatusCode(Exception):
    """The request returned an unexpected status code"""


class MediaNotFound(Exception):
    """No media page was found for the target media"""


class StreamtapeParsingError(Exception):
    """Error getting the video stream from the streamtape page"""
