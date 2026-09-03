"""Route local search to SearXNG and all other engine calls to Fire Engine."""

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlencode, urlparse
from urllib.request import Request, urlopen

SEARX = "http://searxng:8080"
FIRE_ENGINE = "http://host.docker.internal:3010"


def searx_results(payload, v2):
    count = int(payload.get("numResults", payload.get("limit", 10)) or 10)
    params = {"q": payload.get("query", ""), "format": "json", "pageno": payload.get("page", 1)}
    if payload.get("lang"):
        params["language"] = payload["lang"]
    with urlopen(f"{SEARX}/search?{urlencode(params)}", timeout=30) as response:
        raw = json.load(response)
    results = [
        {"url": item.get("url"), "title": item.get("title"), "description": item.get("content", "")}
        for item in raw.get("results", [])[:count]
    ]
    return {"web": results} if v2 else results


def search_payload_from_query(path):
    query = parse_qs(urlparse(path).query)
    payload = {
        "query": (query.get("q") or query.get("query") or [""])[0],
        "limit": (query.get("numResults") or query.get("limit") or [10])[0],
        "page": (query.get("page") or [1])[0],
    }
    language = (query.get("lang") or query.get("language") or [None])[0]
    if language:
        payload["lang"] = language
    return payload


class Router(BaseHTTPRequestHandler):
    def do_POST(self):
        size = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(size)
        if self.path in ("/search", "/v2/search"):
            self._search(json.loads(body or b"{}"), self.path == "/v2/search")
            return
        self._forward("POST", body)

    def do_GET(self):
        route = urlparse(self.path).path
        if route in ("/search", "/v2/search"):
            self._search(search_payload_from_query(self.path), route == "/v2/search")
            return
        self._forward("GET")

    def _search(self, payload, v2):
        try:
            self._write(200, searx_results(payload, v2))
        except Exception as error:
            self._write(502, {"error": f"SearXNG search failed: {error}"})

    def _forward(self, method, body=None):
        try:
            request = Request(FIRE_ENGINE + self.path, data=body, method=method)
            with urlopen(request, timeout=60) as response:
                self._write(response.status, json.load(response))
        except Exception as error:
            self._write(502, {"error": f"Fire Engine proxy failed: {error}"})

    def _write(self, status, value):
        encoded = json.dumps(value).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, *_args):
        return


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", 8088), Router).serve_forever()
