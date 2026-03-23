import http.server
import markdown
import os

MD_FILE = os.path.join(os.path.dirname(__file__), "FC_General_Inquiry_Deep_Dive_Wk8_Wk9.md")

class MDHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        with open(MD_FILE, encoding="utf-8") as f:
            md_text = f.read()
        html_body = markdown.markdown(md_text, extensions=["tables", "fenced_code"])
        html = f"""<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<title>FC General Inquiry Deep Dive</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
         max-width: 960px; margin: 40px auto; padding: 0 20px; line-height: 1.6; color: #1a1a1a; }}
  table {{ border-collapse: collapse; width: 100%; margin: 1em 0; }}
  th, td {{ border: 1px solid #ddd; padding: 8px 12px; text-align: left; }}
  th {{ background: #f5f5f5; font-weight: 600; }}
  tr:nth-child(even) {{ background: #fafafa; }}
  blockquote {{ border-left: 4px solid #0066cc; margin: 1em 0; padding: 0.5em 1em; background: #f0f7ff; }}
  h1 {{ border-bottom: 2px solid #0066cc; padding-bottom: 0.3em; }}
  h2 {{ border-bottom: 1px solid #eee; padding-bottom: 0.2em; margin-top: 2em; }}
  h3 {{ color: #0066cc; }}
  hr {{ border: none; border-top: 1px solid #ddd; margin: 2em 0; }}
  code {{ background: #f0f0f0; padding: 2px 6px; border-radius: 3px; font-size: 0.9em; }}
  strong {{ color: #0a0a0a; }}
</style>
</head><body>{html_body}</body></html>"""
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))
    def log_message(self, format, *args):
        pass

print("Serving preview at http://localhost:8899")
http.server.HTTPServer(("127.0.0.1", 8899), MDHandler).serve_forever()
