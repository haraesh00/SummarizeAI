import pytest

from app.services.article_extractor import URLValidationError, validate_url


def test_validate_url_accepts_https():
    assert validate_url("https://example.com/article", 2048) == "https://example.com/article"


def test_validate_url_rejects_file_scheme():
    with pytest.raises(URLValidationError):
        validate_url("file:///etc/passwd", 2048)


def test_validate_url_rejects_localhost():
    with pytest.raises(URLValidationError):
        validate_url("http://localhost/article", 2048)


def test_validate_url_rejects_private_ip():
    with pytest.raises(URLValidationError):
        validate_url("http://192.168.1.1/article", 2048)


def test_validate_url_rejects_too_long():
    with pytest.raises(URLValidationError):
        validate_url("https://example.com/" + "a" * 3000, 100)
