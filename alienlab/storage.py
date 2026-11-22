"""Protocolo local append-only para hipóteses e execuções."""
from __future__ import annotations
import json
import sqlite3
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_DB = Path(__file__).resolve().parents[1] / "local_data" / "laboratorio.sqlite"

def now():
    return datetime.now(timezone.utc).isoformat()

def git_commit() -> str | None:
    root = Path(__file__).resolve().parents[1]
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root,
                                       stderr=subprocess.DEVNULL, text=True, timeout=3).strip()
    except (OSError, subprocess.SubprocessError):
        return None

def connect(db=DEFAULT_DB):
    db = Path(db)
    db.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(db)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys=ON")
    con.executescript("""
    CREATE TABLE IF NOT EXISTS hypotheses (
      id TEXT PRIMARY KEY, created_utc TEXT NOT NULL, title TEXT NOT NULL,
      claim TEXT NOT NULL, null_hypothesis TEXT NOT NULL,
      prediction TEXT NOT NULL, falsification TEXT NOT NULL,
      confounders TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'registrada');
    CREATE TABLE IF NOT EXISTS runs (
      id TEXT PRIMARY KEY, created_utc TEXT NOT NULL, hypothesis_id TEXT NOT NULL,
      data_origin TEXT NOT NULL, data_sha256 TEXT NOT NULL,
      parameters_json TEXT NOT NULL, results_json TEXT NOT NULL,
      git_sha TEXT, notes TEXT NOT NULL,
      FOREIGN KEY(hypothesis_id) REFERENCES hypotheses(id));
    """)
    con.commit()
    return con

def register_hypothesis(db, *, title, claim, null_hypothesis, prediction,
                        falsification, confounders):
    fields = (title, claim, null_hypothesis, prediction, falsification, confounders)
    if any(not f.strip() for f in fields):
        raise ValueError("Preencha todos os campos científicos da hipótese")
    identifier = "H-" + uuid.uuid4().hex[:12]
    with connect(db) as con:
        con.execute("INSERT INTO hypotheses VALUES (?,?,?,?,?,?,?,?,?)",
                    (identifier, now(), *[f.strip() for f in fields], "registrada"))
    return identifier

def save_run(db, *, hypothesis_id, data_origin, data_sha256, parameters, results, notes=""):
    if not data_origin.strip() or len(data_sha256) != 64 or any(c not in "0123456789abcdef" for c in data_sha256):
        raise ValueError("Origem e SHA-256 válidos são obrigatórios")
    identifier = "E-" + uuid.uuid4().hex[:12]
    with connect(db) as con:
        con.execute("INSERT INTO runs VALUES (?,?,?,?,?,?,?,?,?)",
                    (identifier, now(), hypothesis_id, data_origin.strip(), data_sha256,
                     json.dumps(parameters, ensure_ascii=False, sort_keys=True),
                     json.dumps(results, ensure_ascii=False, sort_keys=True), git_commit(), notes))
        con.execute("UPDATE hypotheses SET status='testada_exploratoriamente' WHERE id=?",
                    (hypothesis_id,))
    return identifier

def list_rows(db, table):
    if table not in ("hypotheses", "runs"):
        raise ValueError("Tabela não permitida")
    with connect(db) as con:
        return [dict(x) for x in con.execute(f"SELECT * FROM {table} ORDER BY created_utc DESC")]

def report_markdown(db):
    hs, runs = list_rows(db, "hypotheses"), list_rows(db, "runs")
    out = ["# AstroVida | Caderno de experimentos", "", f"Gerado em {now()} (UTC).",
           "", "Aviso: significância de contraste não demonstra vida extraterrestre.", ""]
    for h in hs:
        out += [f"## {h['id']}: {h['title']}", "", f"- Alegação: {h['claim']}",
                f"- H0: {h['null_hypothesis']}", f"- Previsão: {h['prediction']}",
                f"- Refutação: {h['falsification']}", f"- Confundidores: {h['confounders']}",
                f"- Status: {h['status']}", ""]
        for run in [r for r in runs if r["hypothesis_id"] == h["id"]]:
            out += [f"### Execução {run['id']}", f"- UTC: {run['created_utc']}",
                    f"- Origem: {run['data_origin']}", f"- SHA256: {run['data_sha256']}",
                    f"- Commit: {run['git_sha'] or 'não disponível'}", "",
                    "```json", json.dumps({"parameters": json.loads(run["parameters_json"]),
                                             "results": json.loads(run["results_json"])},
                                            indent=2, ensure_ascii=False), "```", "",
                    f"- Notas: {run['notes']}", ""]
    return "\n".join(out)
