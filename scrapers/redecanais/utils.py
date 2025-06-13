# utitlity functions

import urllib.parse
import unicodedata
import idna
import re


def convert_to_punycode(url):
    # Decode the URL from percent encoding
    decoded_url = urllib.parse.unquote(url)

    # Parse the URL to extract the domain
    parsed_url = urllib.parse.urlparse(decoded_url)

    # Convert the domain to Punycode
    punycode_domain = idna.encode(parsed_url.netloc).decode("utf-8")

    # Rebuild the URL with the Punycode domain
    punycode_url = urllib.parse.urlunparse(
        (
            parsed_url.scheme,
            punycode_domain,
            parsed_url.path,
            parsed_url.params,
            parsed_url.query,
            parsed_url.fragment,
        )
    )

    return punycode_url


def to_kebab_case(input_string):
    # Normalize unicode characters (convert accented characters to their base form)
    normalized = unicodedata.normalize("NFKD", input_string)

    # Remove diacritical marks (accents) while keeping the base characters
    ascii_str = normalized.encode("ascii", "ignore").decode("ascii")

    # Replace any remaining non-alphanumeric characters with hyphens
    s1 = re.sub(r"[^a-zA-Z0-9]+", "-", ascii_str)

    # Convert to lowercase and strip leading/trailing hyphens
    return s1.lower().strip("-")
