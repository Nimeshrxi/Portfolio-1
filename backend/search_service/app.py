"""Optional Flask microservice for low-latency standalone project search.
Run from backend/: flask --app search_service.app run --port 5001
Set SEARCH_DATA_FILE to a JSON array of project records to index real data.
"""
from flask import Flask, jsonify, request
from portfolio.services.search import ProjectSearchIndex
import json
import os
from pathlib import Path

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False


def load_documents():
    path = os.getenv("SEARCH_DATA_FILE", "")
    if path and Path(path).is_file():
        with open(path, encoding="utf-8") as file:
            payload = json.load(file)
        if isinstance(payload, list):
            return payload
    return [
        {"id": "ownmeet", "slug": "ownmeet", "title": "OwnMeet", "category": "WEB", "short_description": "Online video conferencing application", "tech_stack": ["Python", "WebRTC", "REST APIs"]},
        {"id": "f1-simulator", "slug": "formula-1-management-simulator", "title": "Formula 1 Management Simulator", "category": "DJANGO", "short_description": "Teams, drivers, races and season management", "tech_stack": ["Python", "Django", "PostgreSQL"]},
    ]


search_index = ProjectSearchIndex(load_documents())


@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "portfolio-search", "indexed_documents": len(search_index._documents)})


@app.get("/api/search")
def search():
    query = request.args.get("q", "").strip()[:100]
    if not query:
        return jsonify({"count": 0, "results": []})
    try:
        limit = min(max(int(request.args.get("limit", 20)), 1), 100)
    except ValueError:
        return jsonify({"error": "limit must be an integer"}), 400
    results = search_index.search(query, limit)
    return jsonify({"count": len(results), "results": results})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "5001")), debug=False)
