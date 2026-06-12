import re
import json
import logging
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

def clean_html(html_text: str) -> str:
    """
    Removes HTML tags and normalizes whitespace in the text.
    """
    if not html_text:
        return ""
    # Parse HTML using BeautifulSoup
    soup = BeautifulSoup(html_text, "html.parser")
    # Replace anchor tags with markdown links or just text? 
    # Let's replace anchor tags with their text so they look clean in plain text
    for a in soup.find_all("a"):
        a.replace_with(a.get_text())
        
    text = soup.get_text(separator=" ")
    # Replace multiple spaces/newlines with a single space
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def parse_next_data(html_content: str) -> dict:
    """
    Parses the __NEXT_DATA__ JSON script from the page HTML.
    
    Returns:
        The mfServerSideData dictionary containing the raw mutual fund properties.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    next_data_script = soup.find("script", id="__NEXT_DATA__")
    
    if not next_data_script:
        logger.error("No <script id='__NEXT_DATA__'> element found in the HTML.")
        raise ValueError("Next.js application state script not found in HTML.")
        
    try:
        js_data = json.loads(next_data_script.string)
        mf_data = js_data.get("props", {}).get("pageProps", {}).get("mfServerSideData", {})
        if not mf_data:
            logger.error("mfServerSideData not found in __NEXT_DATA__ props.")
            raise ValueError("mfServerSideData not found in Next.js props.")
        return mf_data
    except Exception as e:
        logger.error(f"Error parsing JSON from __NEXT_DATA__: {e}")
        raise ValueError(f"Failed to parse __NEXT_DATA__: {e}")

def parse_faqs(html_content: str) -> list:
    """
    Extracts FAQs from ld+json scripts of type FAQPage.
    
    Returns:
        A list of dictionaries with 'question' and 'answer' keys.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    faqs = []
    
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            if not script.string:
                continue
            data = json.loads(script.string)
            if data.get("@type") == "FAQPage":
                for item in data.get("mainEntity", []):
                    if item.get("@type") == "Question":
                        q_name = item.get("name", "").strip()
                        answer_data = item.get("acceptedAnswer", {})
                        a_text = answer_data.get("text", "") if answer_data.get("@type") == "Answer" else ""
                        if q_name and a_text:
                            cleaned_a = clean_html(a_text)
                            faqs.append({
                                "question": q_name,
                                "answer": cleaned_a
                            })
        except Exception as e:
            logger.warning(f"Error parsing JSON-LD script for FAQs: {e}")
            
    return faqs

def extract_structured_data(mf_data: dict, faqs: list, scheme_id: str, url: str, scrape_date: str) -> dict:
    """
    Extracts, cleans, and structures relevant mutual fund details into a schema.
    """
    # 1. Base Scheme Info
    scheme_name = mf_data.get("scheme_name") or mf_data.get("fund_name", "")
    
    # 2. Risk Level from return_stats or nfo_risk
    risk = None
    return_stats = mf_data.get("return_stats", [])
    if return_stats and isinstance(return_stats, list):
        risk = return_stats[0].get("risk")
    if not risk:
        risk = mf_data.get("nfo_risk")
        
    # 3. Fund Managers Details
    fund_managers = []
    for mgr in mf_data.get("fund_manager_details", []):
        mgr_name = mgr.get("person_name")
        if mgr_name:
            # Format managed since date if exists
            managed_since = mgr.get("date_from", "")
            if managed_since and "T" in managed_since:
                managed_since = managed_since.split("T")[0]
                
            funds_managed = [fm.get("scheme_name") for fm in mgr.get("funds_managed", []) if fm.get("scheme_name")]
            fund_managers.append({
                "name": mgr_name,
                "education": clean_html(mgr.get("education", "")),
                "experience": clean_html(mgr.get("experience", "")),
                "managed_since": managed_since,
                "funds_managed": funds_managed
            })
            
    # 4. Holdings Details
    holdings = []
    for hld in mf_data.get("holdings", []):
        company_name = hld.get("company_name")
        if company_name:
            holdings.append({
                "company_name": company_name,
                "nature_name": hld.get("nature_name", "Unspecified"),
                "sector_name": hld.get("sector_name", "Unspecified"),
                "instrument_name": hld.get("instrument_name", "Unspecified"),
                "rating": hld.get("rating"),
                "corpus_per": hld.get("corpus_per")
            })

    # 5. Lock-in period parsing
    lock_in_data = mf_data.get("lock_in") or {}
    lock_in_desc = "None"
    if isinstance(lock_in_data, dict):
        parts = []
        if lock_in_data.get("years"):
            parts.append(f"{lock_in_data['years']} Year(s)")
        if lock_in_data.get("months"):
            parts.append(f"{lock_in_data['months']} Month(s)")
        if lock_in_data.get("days"):
            parts.append(f"{lock_in_data['days']} Day(s)")
        if parts:
            lock_in_desc = ", ".join(parts)

    record = {
        "scheme_id": scheme_id,
        "scheme_name": scheme_name,
        "url": url,
        "scrape_date": scrape_date,
        "category": mf_data.get("category"),
        "risk_level": risk,
        "benchmark_name": mf_data.get("benchmark_name") or mf_data.get("benchmark"),
        "nav": mf_data.get("nav"),
        "nav_date": mf_data.get("nav_date"),
        "expense_ratio": mf_data.get("expense_ratio"),
        "exit_load": mf_data.get("exit_load"),
        "aum": mf_data.get("aum"),
        "min_investment": mf_data.get("min_investment_amount"),
        "min_sip": mf_data.get("min_sip_investment"),
        "launch_date": mf_data.get("launch_date"),
        "lock_in": lock_in_desc,
        "investment_objective": mf_data.get("description"),
        "fund_managers": fund_managers,
        "holdings": holdings,
        "faqs": faqs
    }
    
    return record

def build_markdown_document(record: dict) -> str:
    """
    Constructs a structured Markdown document from the parsed mutual fund record.
    """
    md = []
    
    # Title
    md.append(f"# {record['scheme_name']}")
    md.append("")
    
    # Scheme details
    md.append("## Scheme Information")
    md.append(f"- **Scheme Name**: {record['scheme_name']}")
    md.append(f"- **Source URL**: {record['url']}")
    md.append(f"- **Category**: {record['category'] or 'N/A'}")
    md.append(f"- **Risk Level**: {record['risk_level'] or 'N/A'}")
    md.append(f"- **Benchmark**: {record['benchmark_name'] or 'N/A'}")
    md.append(f"- **Launch Date**: {record['launch_date'] or 'N/A'}")
    md.append(f"- **Lock-in Period**: {record['lock_in']}")
    md.append("")
    
    # Fund Metrics
    md.append("## Fund Metrics")
    nav_val = f"₹{record['nav']}" if record['nav'] is not None else "N/A"
    nav_date = f" (as of {record['nav_date']})" if record['nav_date'] else ""
    md.append(f"- **Current NAV**: {nav_val}{nav_date}")
    
    exp_val = f"{record['expense_ratio']}%" if record['expense_ratio'] is not None else "N/A"
    md.append(f"- **Expense Ratio**: {exp_val}")
    
    aum_val = f"₹{record['aum']:,} Cr" if record['aum'] is not None else "N/A"
    md.append(f"- **Assets Under Management (AUM)**: {aum_val}")
    
    min_inv = f"₹{record['min_investment']}" if record['min_investment'] is not None else "N/A"
    md.append(f"- **Minimum Investment (Lumpsum)**: {min_inv}")
    
    min_sip = f"₹{record['min_sip']}" if record['min_sip'] is not None else "N/A"
    md.append(f"- **Minimum SIP Investment**: {min_sip}")
    md.append(f"- **Exit Load**: {record['exit_load'] or 'N/A'}")
    md.append("")
    
    # Investment Objective
    md.append("## Fund Investment Objective")
    md.append(record['investment_objective'] or "No objective described.")
    md.append("")
    
    # Fund Managers
    md.append("## Fund Managers")
    if record['fund_managers']:
        for mgr in record['fund_managers']:
            md.append(f"### {mgr['name']}")
            md.append(f"- **Managed since**: {mgr['managed_since'] or 'N/A'}")
            md.append(f"- **Education**: {mgr['education'] or 'N/A'}")
            md.append(f"- **Experience**: {mgr['experience'] or 'N/A'}")
            if mgr['funds_managed']:
                funds = ", ".join(mgr['funds_managed'])
                md.append(f"- **Other Funds Managed**: {funds}")
            md.append("")
    else:
        md.append("No fund managers listed.")
        md.append("")
        
    # Holdings table
    md.append("## Top Holdings")
    if record['holdings']:
        md.append("| Company | Sector | Nature | Instrument | Rating | Allocation (%) |")
        md.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
        for h in record['holdings']:
            rating = h['rating'] if h['rating'] else "N/A"
            alloc = f"{h['corpus_per']}%" if h['corpus_per'] is not None else "N/A"
            md.append(f"| {h['company_name']} | {h['sector_name']} | {h['nature_name']} | {h['instrument_name']} | {rating} | {alloc} |")
    else:
        md.append("No holdings data listed.")
    md.append("")
    
    # FAQs
    md.append("## Frequently Asked Questions")
    if record['faqs']:
        for faq in record['faqs']:
            md.append(f"### Q: {faq['question']}")
            md.append(f"A: {faq['answer']}")
            md.append("")
    else:
        md.append("No FAQs listed.")
        md.append("")
        
    return "\n".join(md)
