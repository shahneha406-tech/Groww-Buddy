import pytest
from bs4 import BeautifulSoup
from unittest.mock import patch, MagicMock
import requests
from ingestion.scraper import fetch_url
from ingestion.parser import (
    clean_html,
    parse_next_data,
    parse_faqs,
    extract_structured_data,
    build_markdown_document
)
from ingestion.ingest_daily import validate_record

# ----------------- Scraper Tests -----------------

def test_fetch_url_success():
    """Test successful HTML fetch."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "<html><body>Hello World</body></html>"
    
    with patch("requests.get", return_value=mock_response) as mock_get:
        html = fetch_url("https://example.com/fund")
        assert html == "<html><body>Hello World</body></html>"
        mock_get.assert_called_once()

def test_fetch_url_retries_and_fails():
    """Test scraper retry behavior and ultimate failure."""
    with patch("requests.get", side_effect=requests.RequestException("Timeout Error")) as mock_get:
        # Mock time.sleep to avoid waiting during test
        with patch("time.sleep") as mock_sleep:
            with pytest.raises(requests.RequestException):
                fetch_url("https://example.com/fund", retries=3, backoff=0.01)
            assert mock_get.call_count == 3
            assert mock_sleep.call_count == 2

# ----------------- Parser/Normalizer Tests -----------------

def test_clean_html_stripping():
    """Test that clean_html removes HTML tags and collapses spaces."""
    raw_html = "<p>This is <b>bold</b> text.</p>  <br/>  <ul><li>List item 1</li></ul>"
    expected = "This is bold text. List item 1"
    assert clean_html(raw_html) == expected

def test_clean_html_anchor():
    """Test that clean_html extracts anchor text and drops tags."""
    raw_html = "Please check <a href='https://groww.in/p/expense-ratio/'>Expense Ratio</a> charges."
    expected = "Please check Expense Ratio charges."
    assert clean_html(raw_html) == expected

def test_parse_next_data_success():
    """Test parsing of valid __NEXT_DATA__ script."""
    html = """
    <html>
      <script id="__NEXT_DATA__" type="application/json">
        {
          "props": {
            "pageProps": {
              "mfServerSideData": {
                "scheme_name": "Test Mutual Fund",
                "nav": 123.45
              }
            }
          }
        }
      </script>
    </html>
    """
    data = parse_next_data(html)
    assert data["scheme_name"] == "Test Mutual Fund"
    assert data["nav"] == 123.45

def test_parse_next_data_missing():
    """Test parse_next_data raising error when tag is missing."""
    html = "<html><body>No script here</body></html>"
    with pytest.raises(ValueError, match="Next.js application state script not found"):
        parse_next_data(html)

def test_parse_next_data_invalid_json():
    """Test parse_next_data raising error when json is malformed."""
    html = '<html><script id="__NEXT_DATA__" type="application/json">{invalid json</script></html>'
    with pytest.raises(ValueError, match="Failed to parse __NEXT_DATA__"):
        parse_next_data(html)

def test_parse_faqs_success():
    """Test parsing FAQs from JSON-LD script."""
    html = """
    <html>
      <script type="application/ld+json">
        {
          "@context": "https://schema.org",
          "@type": "FAQPage",
          "mainEntity": [
            {
              "@type": "Question",
              "name": "What is NAV?",
              "acceptedAnswer": {
                "@type": "Answer",
                "text": "<p>NAV stands for Net Asset Value.</p>"
              }
            }
          ]
        }
      </script>
    </html>
    """
    faqs = parse_faqs(html)
    assert len(faqs) == 1
    assert faqs[0]["question"] == "What is NAV?"
    assert faqs[0]["answer"] == "NAV stands for Net Asset Value."

def test_extract_structured_data():
    """Test mapping of raw Next.js props and FAQs into schema."""
    raw_props = {
        "scheme_name": "HDFC Mid Cap Fund Direct Growth",
        "category": "Equity - Mid Cap",
        "benchmark_name": "NIFTY Midcap 150 TRI",
        "nav": 220.409,
        "nav_date": "09-Jun-2026",
        "expense_ratio": "0.73",
        "exit_load": "Exit load of 1% if redeemed within 1 year.",
        "aum": 97350.4842,
        "min_investment_amount": 100,
        "min_sip_investment": 100,
        "launch_date": "01-Jan-2013",
        "description": "Long term growth.",
        "lock_in": {"years": 3, "months": 0, "days": 0},
        "return_stats": [{"risk": "Very High", "risk_rating": 6}],
        "fund_manager_details": [
            {
                "person_name": "Chirag Setalvad",
                "education": "MBA",
                "experience": "20 years",
                "date_from": "2012-12-31T18:30:00.000Z",
                "funds_managed": [{"scheme_name": "HDFC Mid Cap"}]
            }
        ],
        "holdings": [
            {
                "company_name": "Repo",
                "nature_name": "CASH",
                "sector_name": "Unspecified",
                "instrument_name": "Repo",
                "rating": None,
                "corpus_per": 6.61
            }
        ]
    }
    
    faqs = [{"question": "Q1", "answer": "A1"}]
    
    record = extract_structured_data(
        raw_props, faqs, "hdfc_mid_cap", "https://groww.in/fund", "2026-06-10"
    )
    
    assert record["scheme_id"] == "hdfc_mid_cap"
    assert record["scheme_name"] == "HDFC Mid Cap Fund Direct Growth"
    assert record["risk_level"] == "Very High"
    assert record["lock_in"] == "3 Year(s)"
    assert len(record["fund_managers"]) == 1
    assert record["fund_managers"][0]["name"] == "Chirag Setalvad"
    assert record["fund_managers"][0]["managed_since"] == "2012-12-31"
    assert record["fund_managers"][0]["funds_managed"] == ["HDFC Mid Cap"]
    assert len(record["holdings"]) == 1
    assert record["holdings"][0]["company_name"] == "Repo"
    assert record["holdings"][0]["corpus_per"] == 6.61
    assert record["faqs"] == faqs

# ----------------- Validation Tests -----------------

def test_validate_record_valid():
    """Test validation with a fully valid record."""
    valid_record = {
        "scheme_id": "test_fund",
        "scheme_name": "Test Fund",
        "nav": 100.5,
        "exit_load": "Nil exit load.",
        "aum": 500.0
    }
    assert validate_record(valid_record) is True

def test_validate_record_missing_name():
    """Test validation failure on missing scheme name."""
    record = {
        "scheme_id": "test_fund",
        "nav": 100.5,
        "exit_load": "Nil exit load.",
        "aum": 500.0
    }
    assert validate_record(record) is False

def test_validate_record_invalid_nav():
    """Test validation failure on negative or missing NAV."""
    record_neg = {
        "scheme_id": "test_fund",
        "scheme_name": "Test Fund",
        "nav": -5.0,
        "exit_load": "Nil exit load.",
        "aum": 500.0
    }
    record_none = {
        "scheme_id": "test_fund",
        "scheme_name": "Test Fund",
        "exit_load": "Nil exit load.",
        "aum": 500.0
    }
    assert validate_record(record_neg) is False
    assert validate_record(record_none) is False

def test_validate_record_missing_exit_load():
    """Test validation failure on missing exit load."""
    record = {
        "scheme_id": "test_fund",
        "scheme_name": "Test Fund",
        "nav": 10.0,
        "aum": 500.0
    }
    assert validate_record(record) is False

# ----------------- Markdown Builder Tests -----------------

def test_build_markdown_document():
    """Test generation of markdown text output from record dict."""
    record = {
        "scheme_id": "hdfc_mid_cap",
        "scheme_name": "HDFC Mid Cap Fund Direct Growth",
        "url": "https://groww.in/fund",
        "category": "Equity - Mid Cap",
        "risk_level": "Very High",
        "benchmark_name": "NIFTY Midcap 150 TRI",
        "nav": 220.409,
        "nav_date": "09-Jun-2026",
        "expense_ratio": "0.73",
        "exit_load": "Exit load of 1% if redeemed within 1 year.",
        "aum": 97350.4842,
        "min_investment": 100,
        "min_sip": 100,
        "launch_date": "01-Jan-2013",
        "lock_in": "None",
        "investment_objective": "Long term growth.",
        "fund_managers": [
            {
                "name": "Chirag Setalvad",
                "managed_since": "2012-12-31",
                "education": "MBA",
                "experience": "20 years",
                "funds_managed": ["HDFC Small Cap"]
            }
        ],
        "holdings": [
            {
                "company_name": "Repo",
                "nature_name": "CASH",
                "sector_name": "Unspecified",
                "instrument_name": "Repo",
                "rating": None,
                "corpus_per": 6.61
            }
        ],
        "faqs": [
            {
                "question": "What is the NAV?",
                "answer": "The NAV is 220.41."
            }
        ]
    }
    
    md_text = build_markdown_document(record)
    
    assert "# HDFC Mid Cap Fund Direct Growth" in md_text
    assert "## Scheme Information" in md_text
    assert "- **Source URL**: https://groww.in/fund" in md_text
    assert "- **Current NAV**: ₹220.409 (as of 09-Jun-2026)" in md_text
    assert "- **Expense Ratio**: 0.73%" in md_text
    assert "- **Assets Under Management (AUM)**: ₹97,350.4842 Cr" in md_text
    assert "## Fund Investment Objective" in md_text
    assert "Long term growth." in md_text
    assert "### Chirag Setalvad" in md_text
    assert "- **Education**: MBA" in md_text
    assert "| Company | Sector | Nature | Instrument | Rating | Allocation (%) |" in md_text
    assert "| Repo | Unspecified | CASH | Repo | N/A | 6.61% |" in md_text
    assert "### Q: What is the NAV?" in md_text
    assert "A: The NAV is 220.41." in md_text
