import os
import json
import urllib.request
import urllib.error
from http.server import SimpleHTTPRequestHandler, HTTPServer
import db

# Simple .env parser to load API keys
def load_env():
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, val = line.split('=', 1)
                    os.environ[key.strip()] = val.strip()

load_env()

class APIProxyHandler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        # Get the path from the super class, which is relative to the current working directory
        translated = super().translate_path(path)
        # Map it to the 'public' directory
        rel_path = os.path.relpath(translated, os.getcwd())
        return os.path.join(os.getcwd(), 'public', rel_path)

    def do_GET(self):
        if self.path == '/favicon.ico':
            self.send_response(204)
            self.end_headers()
            return

        if self.path == '/api/db/schema':
            try:
                schema = db.get_tables_schema()
                self.send_json_response(200, schema)
            except Exception as e:
                self.send_json_response(500, {'error': str(e)})
        elif self.path.startswith('/api/db/data'):
            from urllib.parse import urlparse, parse_qs
            parsed = urlparse(self.path)
            params = parse_qs(parsed.query)
            table = params.get('table', [None])[0]
            
            if not table:
                self.send_json_response(400, {'error': 'Tabellenname fehlt.'})
                return
                
            try:
                data = db.get_table_data(table)
                self.send_json_response(200, data)
            except Exception as e:
                self.send_json_response(500, {'error': str(e)})
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == '/api/ask':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                request_data = json.loads(post_data.decode('utf-8'))
                question = request_data.get('question')
                model = 'gpt-4.1-mini'
                
                if not question:
                    self.send_json_response(400, {'error': 'Bitte stelle eine Frage.'})
                    return
                
                api_key = os.environ.get('OPENAI_API_KEY')
                if not api_key:
                    self.send_json_response(500, {'error': 'API-Key nicht in .env konfiguriert.'})
                    return
                
                # OpenAI Request body
                openai_payload = {
                    "model": model,
                    "messages": [
                        {"role": "user", "content": question}
                    ]
                }
                
                req = urllib.request.Request(
                    'https://api.openai.com/v1/chat/completions',
                    data=json.dumps(openai_payload).encode('utf-8'),
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {api_key}'
                    },
                    method='POST'
                )
                
                try:
                    with urllib.request.urlopen(req) as response:
                        res_data = response.read().decode('utf-8')
                        openai_json = json.loads(res_data)
                        reply = openai_json['choices'][0]['message']['content']
                        self.send_json_response(200, {'reply': reply})
                except urllib.error.HTTPError as e:
                    err_body = e.read().decode('utf-8')
                    try:
                        err_json = json.loads(err_body)
                        err_msg = err_json.get('error', {}).get('message', str(e))
                        err_details = err_json.get('error', {})
                    except Exception:
                        err_msg = str(e)
                        err_details = {}
                    
                    self.send_json_response(e.code, {'error': err_msg, 'details': err_details})
                except Exception as e:
                    self.send_json_response(500, {'error': f'Verbindungsfehler: {str(e)}'})
                    
            except Exception as e:
                self.send_json_response(400, {'error': f'Ungültiger Request: {str(e)}'})
        elif self.path == '/api/db/add-column':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                req_data = json.loads(post_data.decode('utf-8'))
                table = req_data.get('table')
                name = req_data.get('name')
                col_type = req_data.get('type', 'TEXT')
                
                db.add_column_to_table(table, name, col_type)
                self.send_json_response(200, {'success': True, 'message': f'Spalte {name} zu {table} hinzugefuegt.'})
            except Exception as e:
                self.send_json_response(400, {'error': str(e)})
        elif self.path == '/api/db/insert':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                req_data = json.loads(post_data.decode('utf-8'))
                table = req_data.get('table')
                row_data = req_data.get('data')
                
                new_id = db.insert_row(table, row_data)
                self.send_json_response(200, {'success': True, 'id': new_id})
            except Exception as e:
                self.send_json_response(400, {'error': str(e)})
        else:
            self.send_json_response(404, {'error': 'Not Found'})

    def send_json_response(self, code, data):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

def run(port=3000):
    db.init_db()
    server_address = ('', port)
    httpd = HTTPServer(server_address, APIProxyHandler)
    print(f"Server laeuft unter http://localhost:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer wird beendet...")
        httpd.server_close()

if __name__ == '__main__':
    run()
