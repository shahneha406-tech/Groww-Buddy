import sys
import os
from dotenv import load_dotenv

# Add root folder to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.stdout.reconfigure(encoding='utf-8')

# Load .env variables
load_dotenv()

from retrieval.query_engine import MutualFundQueryEngine

def test_live():
    print("Initializing Query Engine...")
    engine = MutualFundQueryEngine()
    
    queries = [
        "What is the exit load of HDFC Small Cap Fund?",
        "Who is the fund manager of HDFC Defence Fund?"
    ]
    
    for q in queries:
        print("\n" + "="*80)
        print(f"QUERY: {q}")
        print("="*80)
        
        response = engine.query(q)
        print("RESPONSE:")
        print(response)

if __name__ == "__main__":
    test_live()
