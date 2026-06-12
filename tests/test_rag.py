import pytest
from unittest.mock import MagicMock
from retrieval.retriever import MutualFundRetriever
from validation.validator import ResponseValidator
from formatter.formatter import ResponseFormatter
from retrieval.query_engine import MutualFundQueryEngine
from retrieval.llm_client import GroqClient

def test_retriever_scheme_detection():
    retriever = MutualFundRetriever()
    
    # Test valid scheme detections
    assert retriever.detect_scheme("What is the exit load of HDFC Small Cap Fund?") == "hdfc_small_cap"
    assert retriever.detect_scheme("Who is the fund manager of HDFC Defence Fund?") == "hdfc_defence"
    assert retriever.detect_scheme("What is the expense ratio of HDFC Top 100 Fund?") == "hdfc_large_cap"
    assert retriever.detect_scheme("HDFC Mid Cap Direct Growth NAV?") == "hdfc_mid_cap"
    assert retriever.detect_scheme("How has the HDFC Gold ETF Fund of Fund performed?") == "hdfc_gold_foh"
    
    # Test no scheme detected
    assert retriever.detect_scheme("Compare exit loads of all these funds.") is None

def test_response_validator():
    validator = ResponseValidator()
    mock_chunks = [{"metadata": {"source_url": "https://test.com"}}]
    
    # Factual response, valid length (2 sentences)
    valid_resp = "HDFC Small Cap Fund was launched on 01-Jan-2013. It has Chirag Setalvad as fund manager."
    is_valid, final_resp = validator.validate(valid_resp, mock_chunks)
    assert is_valid is True
    assert final_resp == valid_resp
    
    # Too long response (4 sentences)
    too_long_resp = "This is sentence one. This is sentence two. This is sentence three. This is sentence four."
    is_valid, final_resp = validator.validate(too_long_resp, mock_chunks)
    assert is_valid is False
    assert final_resp == "I cannot find this information in the official documents."
    
    # Advisory response
    advisory_resp = "HDFC Small Cap Fund is the best fund. You should invest in it."
    is_valid, final_resp = validator.validate(advisory_resp, mock_chunks)
    assert is_valid is False
    assert "cannot provide investment advice" in final_resp

def test_response_formatter():
    formatter = ResponseFormatter()
    mock_chunks = [
        {
            "metadata": {
                "source_url": "https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth",
                "last_updated_date": "2026-06-10"
            }
        }
    ]
    txt = "The exit load is 1%."
    formatted = formatter.format(txt, mock_chunks)
    
    assert "The exit load is 1%." in formatted
    assert "Source: https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth" in formatted
    assert "Last updated from sources: 2026-06-10" in formatted

def test_query_engine_integration(monkeypatch):
    # Mock LLM Client generate_answer method to return a predefined response
    mock_response = "The exit load of HDFC Small Cap Fund is 1% if redeemed within 1 year."
    
    def mock_generate_answer(self, query, retrieved_chunks):
        return mock_response
        
    monkeypatch.setattr(GroqClient, "generate_answer", mock_generate_answer)
    
    engine = MutualFundQueryEngine()
    
    # Run query
    response = engine.query("What is the exit load of HDFC Small Cap Fund?")
    
    # Assertions
    assert "The exit load of HDFC Small Cap Fund is 1" in response
    assert "Source: https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth" in response
    assert "Last updated from sources: 2026-06-" in response

def test_query_engine_pii_blocking():
    engine = MutualFundQueryEngine()
    
    # Email query
    resp1 = engine.query("My email is user@domain.com. What is the NAV?")
    assert "cannot process queries containing personal identifier information" in resp1
    
    # PAN query
    resp2 = engine.query("My PAN is ABCDE1234F. Show exit load.")
    assert "cannot process queries containing personal identifier information" in resp2

def test_query_engine_advisory_blocking():
    engine = MutualFundQueryEngine()
    
    # Recommending query
    resp1 = engine.query("Which fund would you recommend for me?")
    assert "cannot provide investment recommendations" in resp1
    
    # Advice query
    resp2 = engine.query("Should I buy HDFC Defence Fund?")
    assert "cannot provide investment recommendations" in resp2

def test_query_engine_out_of_scope_blocking():
    engine = MutualFundQueryEngine()
    
    resp = engine.query("What is Next Leap?")
    assert "specialized assistant for HDFC Mutual Funds" in resp
    assert "outside this domain" in resp

def test_query_engine_greetings_handling():
    engine = MutualFundQueryEngine()
    
    resp = engine.query("Hello")
    assert "factual HDFC Mutual Fund FAQ assistant" in resp
    assert "How can I help you today" in resp
