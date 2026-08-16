import ipaddress
import socket
from dataclasses import dataclass
from urllib.parse import urlparse

import httpx
import trafilatura

from app.config import Settings


class ArticleExtractionError(Exception):
    pass


class URLValidationError(Exception):
    pass


@dataclass
class ExtractedArticle:
    title: str | None
    text: str
    url: str


def _is_blocked_ip(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    return (
        ip.is_loopback
        or ip.is_private
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
    )


def validate_url(url: str, max_length: int) -> str:
    if len(url) > max_length:
        raise URLValidationError("URL exceeds maximum allowed length.")

    parsed = urlparse(url.strip())
    if parsed.scheme not in ("http", "https"):
        raise URLValidationError("Only http and https URLs are supported.")
    if not parsed.hostname:
        raise URLValidationError("Invalid URL.")

    hostname = parsed.hostname.lower()
    blocked_hostnames = {"localhost", "127.0.0.1", "0.0.0.0", "::1"}
    if hostname in blocked_hostnames or hostname.endswith(".local"):
        raise URLValidationError("URL target is not allowed.")

    try:
        addr_infos = socket.getaddrinfo(hostname, parsed.port or 443, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise URLValidationError("Unable to resolve URL hostname.") from exc

    for info in addr_infos:
        ip_str = info[4][0]
        ip = ipaddress.ip_address(ip_str)
        if _is_blocked_ip(ip):
            raise URLValidationError("URL target is not allowed.")

    return url.strip()


async def fetch_and_extract(url: str, settings: Settings) -> ExtractedArticle:
    validate_url(url, settings.max_url_length)

    timeout = httpx.Timeout(
        connect=settings.fetch_connect_timeout,
        read=settings.fetch_read_timeout,
        write=settings.fetch_read_timeout,
        pool=settings.fetch_connect_timeout,
    )

    async with httpx.AsyncClient(
        timeout=timeout,
        follow_redirects=True,
        headers={"User-Agent": "AI-Summarizer/1.0"},
    ) as client:
        async with client.stream("GET", url) as response:
            response.raise_for_status()
            content_type = response.headers.get("content-type", "")
            if "text/html" not in content_type and "application/xhtml" not in content_type:
                raise ArticleExtractionError(
                    "Unable to extract article text from the supplied URL."
                )

            chunks: list[bytes] = []
            total = 0
            async for chunk in response.aiter_bytes():
                total += len(chunk)
                if total > settings.fetch_max_bytes:
                    raise ArticleExtractionError(
                        "Unable to extract article text from the supplied URL."
                    )
                chunks.append(chunk)

            html = b"".join(chunks).decode("utf-8", errors="replace")

    extracted = trafilatura.extract(
        html,
        url=url,
        include_comments=False,
        include_tables=False,
        output_format="txt",
    )
    if not extracted or len(extracted.strip()) < 100:
        raise ArticleExtractionError(
            "Unable to extract article text from the supplied URL."
        )

    metadata = trafilatura.extract_metadata(html, default_url=url)
    title = metadata.title if metadata else None

    return ExtractedArticle(title=title, text=extracted.strip(), url=url)
