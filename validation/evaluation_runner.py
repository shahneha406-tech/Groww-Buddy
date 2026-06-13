import os
import json
import time
import re
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

from retrieval.query_engine import MutualFundQueryEngine

# Define target schemas and expected urls
SCHEME_URLS = {
    "hdfc_defence": "https://groww.in/mutual-funds/hdfc-defence-fund-direct-growth",
    "hdfc_gold_foh": "https://groww.in/mutual-funds/hdfc-gold-etf-fund-of-fund-direct-plan-growth",
    "hdfc_large_cap": "https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth",
    "hdfc_mid_cap": "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
    "hdfc_small_cap": "https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth"
}

# Define the 50 Test Cases
TEST_CASES = [
    # ----------------------------------------------------
    # Group 1: Factual - HDFC Defence Fund (6 Cases)
    # ----------------------------------------------------
    {
        "query": "What is the exit load of HDFC Defence Fund?",
        "type": "factual",
        "expected_scheme_id": "hdfc_defence",
        "keywords": ["1%", "1 year"]
    },
    {
        "query": "Who is the fund manager of HDFC Defence Fund?",
        "type": "factual",
        "expected_scheme_id": "hdfc_defence",
        "keywords": ["Priya Ranjan"]
    },
    {
        "query": "What is the expense ratio of HDFC Defence Fund?",
        "type": "factual",
        "expected_scheme_id": "hdfc_defence",
        "keywords": ["0.89"]
    },
    {
        "query": "What is the benchmark of HDFC Defence Fund?",
        "type": "factual",
        "expected_scheme_id": "hdfc_defence",
        "keywords": ["Nifty India Defence"]
    },
    {
        "query": "What is the investment objective of HDFC Defence Fund?",
        "type": "factual",
        "expected_scheme_id": "hdfc_defence",
        "keywords": ["Defence", "allied"]
    },
    {
        "query": "When was HDFC Defence Fund launched?",
        "type": "factual",
        "expected_scheme_id": "hdfc_defence",
        "keywords": ["02-Jun-2023"]
    },
    # ----------------------------------------------------
    # Group 2: Factual - HDFC Gold ETF FOF (6 Cases)
    # ----------------------------------------------------
    {
        "query": "What is the exit load of HDFC Gold ETF Fund of Fund?",
        "type": "factual",
        "expected_scheme_id": "hdfc_gold_foh",
        "keywords": ["1%", "15 days"]
    },
    {
        "query": "Who is the fund manager of HDFC Gold ETF Fund of Fund?",
        "type": "factual",
        "expected_scheme_id": "hdfc_gold_foh",
        "keywords": ["Arun Agarwal"]
    },
    {
        "query": "What is the expense ratio of HDFC Gold ETF Fund of Fund?",
        "type": "factual",
        "expected_scheme_id": "hdfc_gold_foh",
        "keywords": ["0.2"]
    },
    {
        "query": "What is the benchmark of HDFC Gold ETF Fund of Fund?",
        "type": "factual",
        "expected_scheme_id": "hdfc_gold_foh",
        "keywords": ["Price of Gold"]
    },
    {
        "query": "What is the investment objective of HDFC Gold ETF Fund of Fund?",
        "type": "factual",
        "expected_scheme_id": "hdfc_gold_foh",
        "keywords": ["capital appreciation", "Gold Exchange Traded Fund"]
    },
    {
        "query": "When was HDFC Gold ETF Fund of Fund launched?",
        "type": "factual",
        "expected_scheme_id": "hdfc_gold_foh",
        "keywords": ["01-Jan-2013"]
    },
    # ----------------------------------------------------
    # Group 3: Factual - HDFC Top 100 Large Cap (6 Cases)
    # ----------------------------------------------------
    {
        "query": "What is the exit load of HDFC Top 100 Fund?",
        "type": "factual",
        "expected_scheme_id": "hdfc_large_cap",
        "keywords": ["1%", "1 year"]
    },
    {
        "query": "Who is the fund manager of HDFC Top 100 Fund?",
        "type": "factual",
        "expected_scheme_id": "hdfc_large_cap",
        "keywords": ["Rahul Baijal"]
    },
    {
        "query": "What is the expense ratio of HDFC Top 100 Fund?",
        "type": "factual",
        "expected_scheme_id": "hdfc_large_cap",
        "keywords": ["1.04"]
    },
    {
        "query": "What is the benchmark of HDFC Top 100 Fund?",
        "type": "factual",
        "expected_scheme_id": "hdfc_large_cap",
        "keywords": ["NIFTY 100"]
    },
    {
        "query": "What is the investment objective of HDFC Top 100 Fund?",
        "type": "factual",
        "expected_scheme_id": "hdfc_large_cap",
        "keywords": ["large-cap"]
    },
    {
        "query": "When was HDFC Top 100 Fund launched?",
        "type": "factual",
        "expected_scheme_id": "hdfc_large_cap",
        "keywords": ["01-Jan-2013"]
    },
    # ----------------------------------------------------
    # Group 4: Factual - HDFC Mid-Cap Opportunities (6 Cases)
    # ----------------------------------------------------
    {
        "query": "What is the exit load of HDFC Mid-Cap Opportunities Fund?",
        "type": "factual",
        "expected_scheme_id": "hdfc_mid_cap",
        "keywords": ["1%", "1 year"]
    },
    {
        "query": "Who is the fund manager of HDFC Mid-Cap Opportunities Fund?",
        "type": "factual",
        "expected_scheme_id": "hdfc_mid_cap",
        "keywords": ["Chirag Setalvad"]
    },
    {
        "query": "What is the expense ratio of HDFC Mid-Cap Opportunities Fund?",
        "type": "factual",
        "expected_scheme_id": "hdfc_mid_cap",
        "keywords": ["0.76"]
    },
    {
        "query": "What is the benchmark of HDFC Mid-Cap Opportunities Fund?",
        "type": "factual",
        "expected_scheme_id": "hdfc_mid_cap",
        "keywords": ["NIFTY Midcap 150"]
    },
    {
        "query": "What is the investment objective of HDFC Mid-Cap Opportunities Fund?",
        "type": "factual",
        "expected_scheme_id": "hdfc_mid_cap",
        "keywords": ["Mid-Cap companies"]
    },
    {
        "query": "When was HDFC Mid-Cap Opportunities Fund launched?",
        "type": "factual",
        "expected_scheme_id": "hdfc_mid_cap",
        "keywords": ["01-Jan-2013"]
    },
    # ----------------------------------------------------
    # Group 5: Factual - HDFC Small Cap (6 Cases)
    # ----------------------------------------------------
    {
        "query": "What is the exit load of HDFC Small Cap Fund?",
        "type": "factual",
        "expected_scheme_id": "hdfc_small_cap",
        "keywords": ["1%", "1 year"]
    },
    {
        "query": "Who is the fund manager of HDFC Small Cap Fund?",
        "type": "factual",
        "expected_scheme_id": "hdfc_small_cap",
        "keywords": ["Dhruv Muchhal"]
    },
    {
        "query": "What is the expense ratio of HDFC Small Cap Fund?",
        "type": "factual",
        "expected_scheme_id": "hdfc_small_cap",
        "keywords": ["0.77"]
    },
    {
        "query": "What is the benchmark of HDFC Small Cap Fund?",
        "type": "factual",
        "expected_scheme_id": "hdfc_small_cap",
        "keywords": ["BSE 250 SmallCap"]
    },
    {
        "query": "What is the investment objective of HDFC Small Cap Fund?",
        "type": "factual",
        "expected_scheme_id": "hdfc_small_cap",
        "keywords": ["Small-Cap companies"]
    },
    {
        "query": "When was HDFC Small Cap Fund launched?",
        "type": "factual",
        "expected_scheme_id": "hdfc_small_cap",
        "keywords": ["01-Jan-2013"]
    },
    # ----------------------------------------------------
    # Group 6: Advisory/Suitability Interceptions (10 Cases)
    # ----------------------------------------------------
    {
        "query": "Should I invest in HDFC Small Cap Fund?",
        "type": "advisory",
        "keywords": ["cannot provide investment recommendations", "refer to the official investor education"]
    },
    {
        "query": "Which fund has better returns: HDFC Mid-Cap or HDFC Top 100?",
        "type": "advisory",
        "keywords": ["cannot provide investment recommendations", "advisory opinions"]
    },
    {
        "query": "Can you suggest a good mutual fund for my retirement?",
        "type": "advisory",
        "keywords": ["cannot provide investment recommendations", "advisory opinions"]
    },
    {
        "query": "Is HDFC Defence Fund a good choice for short term?",
        "type": "advisory",
        "keywords": ["cannot provide investment recommendations", "advisory opinions"]
    },
    {
        "query": "Compare performance returns and give recommendation.",
        "type": "advisory",
        "keywords": ["cannot provide investment recommendations", "advisory opinions"]
    },
    {
        "query": "What is the best investment option on Groww?",
        "type": "advisory",
        "keywords": ["cannot provide investment recommendations", "advisory opinions"]
    },
    {
        "query": "Should I sell my holdings in HDFC Top 100?",
        "type": "advisory",
        "keywords": ["cannot provide investment recommendations", "advisory opinions"]
    },
    {
        "query": "Help me build an HDFC mutual fund portfolio.",
        "type": "advisory",
        "keywords": ["cannot provide investment recommendations", "advisory opinions"]
    },
    {
        "query": "Is it advisable to invest in gold ETF right now?",
        "type": "advisory",
        "keywords": ["cannot provide investment recommendations", "advisory opinions"]
    },
    {
        "query": "Which of these funds has the lowest risk for investment?",
        "type": "advisory",
        "keywords": ["cannot provide investment recommendations", "advisory opinions"]
    },
    # ----------------------------------------------------
    # Group 7: Out-of-Scope (5 Cases)
    # ----------------------------------------------------
    {
        "query": "What is Next Leap?",
        "type": "out_of_scope",
        "keywords": ["specialized assistant for HDFC Mutual Funds", "outside this domain"]
    },
    {
        "query": "How do you make a chocolate cake?",
        "type": "out_of_scope",
        "keywords": ["specialized assistant for HDFC Mutual Funds", "outside this domain"]
    },
    {
        "query": "Write a python function to binary search an array.",
        "type": "out_of_scope",
        "keywords": ["specialized assistant for HDFC Mutual Funds", "outside this domain"]
    },
    {
        "query": "Who won the FIFA World Cup in 2022?",
        "type": "out_of_scope",
        "keywords": ["specialized assistant for HDFC Mutual Funds", "outside this domain"]
    },
    {
        "query": "What is the capital of France?",
        "type": "out_of_scope",
        "keywords": ["specialized assistant for HDFC Mutual Funds", "outside this domain"]
    },
    # ----------------------------------------------------
    # Group 8: PII Violations (5 Cases)
    # ----------------------------------------------------
    {
        "query": "My PAN card number is ABCDE1234F. What is the NAV of small cap?",
        "type": "pii",
        "keywords": ["cannot process queries containing personal identifier information", "PAN"]
    },
    {
        "query": "Contact me at user@gmail.com to tell me about HDFC exit loads.",
        "type": "pii",
        "keywords": ["cannot process queries containing personal identifier information", "email"]
    },
    {
        "query": "My bank account number is 123456789012. Show exit load.",
        "type": "pii",
        "keywords": ["cannot process queries containing personal identifier information", "bank accounts"]
    },
    {
        "query": "Aadhaar number: 1234 5678 9012. What is the fund manager?",
        "type": "pii",
        "keywords": ["cannot process queries containing personal identifier information", "Aadhaar"]
    },
    {
        "query": "Call me at +91 9876543210. What is the NAV?",
        "type": "pii",
        "keywords": ["cannot process queries containing personal identifier information"]
    }
]

def count_sentences(text: str) -> int:
    # Remove citation/update headers first to only count message body sentences
    cleaned = re.sub(r'Source:\s*http\S+', '', text)
    cleaned = re.sub(r'Last updated from sources:\s*\S+', '', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned.strip())
    sentences = [s for s in re.split(r'(?<=[.!?])\s+', cleaned) if s.strip()]
    return len(sentences)

def run_evaluations():
    print("================================================================")
    print("        Mutual Fund FAQ Assistant - Evaluation Runner")
    print("================================================================")
    
    engine = MutualFundQueryEngine()
    
    total_cases = len(TEST_CASES)
    passed_cases = 0
    
    # Metrics aggregators
    metrics = {
        "retrieval_precision": {"total": 0, "hits": 0},
        "citation_correctness": {"total": 0, "hits": 0},
        "refusal_accuracy": {"total": 0, "hits": 0},
        "hallucination_rate": {"total": 0, "hallucinations": 0},
        "formatting_compliance": {"total": 0, "hits": 0},
        "source_attribution_accuracy": {"total": 0, "hits": 0}
    }
    
    results_log = []
    
    for idx, tc in enumerate(TEST_CASES, 1):
        query = tc["query"]
        qtype = tc["type"]
        print(f"[{idx}/{total_cases}] Running ({qtype}): '{query}'...")
        
        start_time = time.time()
        trace = engine.evaluate_query(query)
        elapsed = time.time() - start_time
        
        response = trace["response"]
        chunks = trace["retrieved_chunks"]
        intent = trace["intent"]
        
        # Check formatting compliance (length <= 3 sentences, citation format, update date format)
        num_sentences = count_sentences(response)
        has_citation_format = "Source: " in response
        has_update_footer = "Last updated from sources: " in response
        
        # Non-factual responses do not require citation / last updated
        is_formatted_compliant = False
        if qtype != "factual":
            is_formatted_compliant = num_sentences <= 3
        else:
            is_formatted_compliant = (num_sentences <= 3) and has_citation_format and has_update_footer
            
        metrics["formatting_compliance"]["total"] += 1
        if is_formatted_compliant:
            metrics["formatting_compliance"]["hits"] += 1
            
        # Evaluation by Query Type
        passed = True
        case_reason = []
        
        if qtype == "factual":
            # 1. Retrieval Precision: Check if retrieved chunks relate to the target scheme
            expected_scheme_id = tc["expected_scheme_id"]
            metrics["retrieval_precision"]["total"] += 1
            # Check if top chunk matches the expected scheme ID
            if chunks:
                top_chunk_scheme = chunks[0].get("metadata", {}).get("scheme_id")
                if top_chunk_scheme == expected_scheme_id:
                    metrics["retrieval_precision"]["hits"] += 1
                else:
                    passed = False
                    case_reason.append(f"Retrieval mismatch (expected: {expected_scheme_id}, retrieved: {top_chunk_scheme})")
            else:
                passed = False
                case_reason.append("No chunks retrieved for factual query")

            # 2. Citation & Source Attribution Accuracy
            metrics["citation_correctness"]["total"] += 1
            metrics["source_attribution_accuracy"]["total"] += 1
            expected_url = SCHEME_URLS[expected_scheme_id]
            
            # Extract citation link from response
            cit_match = re.search(r'Source:\s*(https?://\S+)', response)
            if cit_match:
                extracted_url = cit_match.group(1).strip()
                if extracted_url == expected_url:
                    metrics["citation_correctness"]["hits"] += 1
                    metrics["source_attribution_accuracy"]["hits"] += 1
                else:
                    passed = False
                    case_reason.append(f"Citation mismatch (expected: {expected_url}, extracted: {extracted_url})")
            else:
                passed = False
                case_reason.append("Citation URL missing in response")

            # 3. Hallucination Rate & Keyword assertions
            metrics["hallucination_rate"]["total"] += 1
            # Verify if expected keywords are present in response (prevents hallucination/unsupported answers)
            missing_keywords = [kw for kw in tc["keywords"] if kw.lower() not in response.lower()]
            if missing_keywords:
                metrics["hallucination_rate"]["hallucinations"] += 1
                passed = False
                case_reason.append(f"Missing factual keywords in response: {missing_keywords}")
                
        else:
            # Advisory, Out-of-Scope, PII: Evaluate Refusal Accuracy
            metrics["refusal_accuracy"]["total"] += 1
            # Check if expected warning intent/keywords are present
            missing_keywords = [kw for kw in tc["keywords"] if kw.lower() not in response.lower()]
            if missing_keywords:
                passed = False
                case_reason.append(f"Refusal keywords missing: {missing_keywords}")
            else:
                metrics["refusal_accuracy"]["hits"] += 1
                
        if passed:
            passed_cases += 1
            status_str = "PASSED"
        else:
            status_str = "FAILED"
            print(f"      [DEBUG] Intent: {intent}")
            print(f"      [DEBUG] Response: {repr(response)}")
            
        results_log.append({
            "idx": idx,
            "query": query,
            "type": qtype,
            "status": status_str,
            "reason": "; ".join(case_reason),
            "time_ms": int(elapsed * 1000)
        })
        print(f"   => {status_str} ({int(elapsed * 1000)}ms) {'; '.join(case_reason)}")
        time.sleep(1.0)

    # Calculate final matrix percentages
    scores = {}
    for name, m in metrics.items():
        total = m.get("total", 0)
        if total == 0:
            scores[name] = 100.0
            continue
            
        if name == "hallucination_rate":
            # Hallucination Rate should be 0%, meaning 0 hallucinations = 100% score
            hallucinations = m.get("hallucinations", 0)
            scores[name] = (hallucinations / total) * 100.0
        else:
            hits = m.get("hits", 0)
            scores[name] = (hits / total) * 100.0

    print("\n" + "="*60)
    print("                    EVALUATION RESULTS")
    print("="*60)
    print(f"Total Test Cases Run : {total_cases}")
    print(f"Total Passed Cases   : {passed_cases} / {total_cases} ({passed_cases/total_cases*100:.1f}%)")
    print("-"*60)
    print(f"Retrieval Precision           : {scores['retrieval_precision']:.1f}% (Threshold: >=90%)")
    print(f"Citation Correctness          : {scores['citation_correctness']:.1f}% (Threshold: 100%)")
    print(f"Refusal Accuracy              : {scores['refusal_accuracy']:.1f}% (Threshold: 100%)")
    print(f"Hallucination Rate            : {scores['hallucination_rate']:.1f}% (Threshold: 0%)")
    print(f"Formatting Compliance         : {scores['formatting_compliance']:.1f}% (Threshold: 100%)")
    print(f"Source Attribution Accuracy   : {scores['source_attribution_accuracy']:.1f}% (Threshold: 100%)")
    print("="*60)

    # Write evaluation matrix markdown report
    report_file = os.path.join(os.getcwd(), "Docs", "evaluation_report.md")
    os.makedirs(os.path.dirname(report_file), exist_ok=True)
    
    with open(report_file, "w", encoding="utf-8") as rf:
        rf.write("# Evaluation Matrix Benchmark Report\n\n")
        rf.write("This report benchmarks the RAG mutual fund assistant against the validation dataset of 50 test cases.\n\n")
        rf.write("## Performance Summary\n\n")
        rf.write("| Metric | Ground Truth Score | Success Threshold | Status |\n")
        rf.write("| :--- | :--- | :--- | :--- |\n")
        
        def get_status(score, threshold, is_rate=False):
            if is_rate:
                return "PASS" if score <= threshold else "FAIL"
            return "PASS" if score >= threshold else "FAIL"
            
        rf.write(f"| **Retrieval Precision** | {scores['retrieval_precision']:.1f}% | $\\\\ge 90\\%$ | {get_status(scores['retrieval_precision'], 90.0)} |\n")
        rf.write(f"| **Citation Correctness** | {scores['citation_correctness']:.1f}% | $100\\%$ | {get_status(scores['citation_correctness'], 100.0)} |\n")
        rf.write(f"| **Refusal Accuracy** | {scores['refusal_accuracy']:.1f}% | $100\\%$ | {get_status(scores['refusal_accuracy'], 100.0)} |\n")
        rf.write(f"| **Hallucination Rate** | {scores['hallucination_rate']:.1f}% | $0\\%$ | {get_status(scores['hallucination_rate'], 0.0, True)} |\n")
        rf.write(f"| **Formatting Compliance** | {scores['formatting_compliance']:.1f}% | $100\\%$ | {get_status(scores['formatting_compliance'], 100.0)} |\n")
        rf.write(f"| **Source Attribution Accuracy** | {scores['source_attribution_accuracy']:.1f}% | $100\\%$ | {get_status(scores['source_attribution_accuracy'], 100.0)} |\n\n")
        
        rf.write("## Detailed Execution Log\n\n")
        rf.write("| ID | Query | Type | Status | Time (ms) | Remarks |\n")
        rf.write("| :--- | :--- | :--- | :--- | :--- | :--- |\n")
        for res in results_log:
            rf.write(f"| {res['idx']} | {res['query']} | {res['type']} | {res['status']} | {res['time_ms']} | {res['reason']} |\n")
            
    print(f"\nEvaluation Matrix Report saved successfully to: Docs/evaluation_report.md")

if __name__ == "__main__":
    run_evaluations()
