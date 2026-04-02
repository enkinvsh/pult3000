import pytest

from src.bot.handlers.search import extract_query


class TestExtractQuery:
    def test_extract_with_включи(self):
        assert extract_query("включи Metallica") == "Metallica"

    def test_extract_with_поставь(self):
        assert extract_query("поставь Nothing Else Matters") == "Nothing Else Matters"

    def test_extract_with_играй(self):
        assert extract_query("играй AC/DC Back in Black") == "AC/DC Back in Black"

    def test_extract_strips_whitespace(self):
        assert extract_query("  включи   Metallica  ") == "Metallica"

    def test_extract_returns_none_for_unrecognized(self):
        assert extract_query("привет") is None

    def test_extract_returns_none_for_empty_query(self):
        assert extract_query("включи") is None

    def test_extract_with_найди(self):
        assert extract_query("найди Rammstein Du Hast") == "Rammstein Du Hast"

    def test_raw_text_treated_as_search(self):
        assert (
            extract_query("Metallica Enter Sandman", allow_raw=True)
            == "Metallica Enter Sandman"
        )
