"""Flask-приложение."""

import asyncio
import json
import os
from dataclasses import asdict

from flask import Flask, jsonify, render_template, request

from .aggregate import aggregate
from .engines import ENGINES

app = Flask(__name__)

DEFAULT_ENGINES = ["ddg", "brave"]
MAX_RESULTS = 20


def _run(coro):
    """Запускаем async из sync Flask."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@app.get("/")
def index():
    q = request.args.get("q", "")
    engines = request.args.getlist("engines") or DEFAULT_ENGINES
    engines = [e for e in engines if e in ENGINES]
    results = None
    took_ms = 0
    if q:
        resp = _run(aggregate(q, engines, n=MAX_RESULTS))
        results = resp.results
        took_ms = resp.took_ms
    return render_template(
        "index.html",
        query=q,
        results=results,
        took_ms=took_ms,
        engines=list(ENGINES.keys()),
        active_engines=engines,
    )


@app.get("/api/search")
def api_search():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify({"error": "параметр q обязателен"}), 400
    engines = request.args.getlist("engines") or DEFAULT_ENGINES
    engines = [e for e in engines if e in ENGINES]
    resp = _run(aggregate(q, engines, n=MAX_RESULTS))
    data = asdict(resp)
    return jsonify(data)


@app.get("/health")
def health():
    return jsonify({"ok": True})
