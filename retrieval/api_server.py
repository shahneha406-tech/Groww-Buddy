import os
import json
import traceback
from http.server import HTTPServer, BaseHTTPRequestHandler
from retrieval.query_engine import MutualFundQueryEngine

class APIRequestHandler(BaseHTTPRequestHandler):
    query_engine = None

    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        # Enable CORS for React frontend
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(200)

    def do_GET(self):
        if self.path in ('/', '/health'):
            self._set_headers(200)
            self.wfile.write(json.dumps({"status": "healthy", "message": "Groww Buddy API Server is running!"}).encode('utf-8'))
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not Found"}).encode('utf-8'))

    def do_POST(self):
        if self.path == '/api/query':
            try:
                # Read content length
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                req_json = json.loads(post_data.decode('utf-8'))
                
                query_str = req_json.get('query', '')
                if not query_str:
                    self._set_headers(400)
                    self.wfile.write(json.dumps({"error": "Query field is required"}).encode('utf-8'))
                    return
                
                print(f"[API] Processing query: {query_str}")
                # Process query using the query engine
                response_str = self.query_engine.query(query_str)
                
                # Send response
                self._set_headers(200)
                res_payload = {
                    "query": query_str,
                    "response": response_str
                }
                self.wfile.write(json.dumps(res_payload).encode('utf-8'))
                
            except Exception as e:
                print(f"[API] Error: {traceback.format_exc()}")
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not Found"}).encode('utf-8'))

def run_server(port=8000):
    print("Initializing Mutual Fund Query Engine...")
    engine = MutualFundQueryEngine()
    APIRequestHandler.query_engine = engine
    
    server_address = ('', port)
    httpd = HTTPServer(server_address, APIRequestHandler)
    print(f"API Server running on port {port}...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Stopping server...")
        httpd.server_close()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    run_server(port=port)
