# services/report_generator.py
from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List, Tuple
from html import escape
import webbrowser

def coerce_date_str(d: Any) -> str:
    if hasattr(d, "isoformat"):
        return d.isoformat()
    return str(d) if d is not None else ""

def split_members(records: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    students, teachers = [], []
    for r in records:
        r = dict(r)
        r.setdefault("full_name", r.get("name", ""))
        r.setdefault("email", "")
        r.setdefault("phone", "")
        r.setdefault("address", "")
        r["join_date"] = coerce_date_str(r.get("join_date"))

        if "student_id" in r and isinstance(r["student_id"], int):
            students.append(r)
        elif "teacher_id" in r and isinstance(r["teacher_id"], int):
            teachers.append(r)
        else:
            pass
    return students, teachers

def build_member_maps(students: List[Dict[str, Any]], teachers: List[Dict[str, Any]]):
    s_map = {r.get("student_id"): r.get("full_name", "") for r in students if "student_id" in r}
    t_map = {r.get("teacher_id"): r.get("full_name", "") for r in teachers if "teacher_id" in r}
    return s_map, t_map

def parse_events(records: List[Dict[str, Any]],
                 student_map: Dict[int, str],
                 teacher_map: Dict[int, str]) -> List[Dict[str, Any]]:
    parsed = []
    for e in records:
        ev = dict(e)
        ev.setdefault("event_name", ev.get("name", ""))
        ev.setdefault("description", "")
        ev["event_date"] = coerce_date_str(ev.get("event_date"))

        org_ids = ev.get("organizer_ids") or ev.get("organizers_ids") or []
        part_ids = ev.get("participant_ids") or ev.get("participants_ids") or []

        if not org_ids and isinstance(ev.get("organizers"), list):
            org_ids = [o.get("teacher_id") for o in ev["organizers"] if isinstance(o, dict)]
        if not part_ids and isinstance(ev.get("participants"), list):
            part_ids = [s.get("student_id") for s in ev["participants"] if isinstance(s, dict)]

        organizers = [teacher_map.get(i, f"Teacher#{i}") for i in org_ids if i is not None]
        participants = [student_map.get(i, f"Student#{i}") for i in part_ids if i is not None]

        parsed.append({
            "event_name": ev["event_name"],
            "event_date": ev["event_date"],
            "description": ev.get("description", ""),
            "organizers": organizers,
            "participants": participants,
        })
    return parsed

def render_table(headers: List[str], rows: List[List[str]]) -> str:
    thead = "".join(f"<th>{escape(h)}</th>" for h in headers)
    trs = []
    for r in rows:
        tds = "".join(f"<td>{escape(str(c))}</td>" for c in r)
        trs.append(f"<tr>{tds}</tr>")
    tbody = "".join(trs) if trs else f"<tr><td colspan='{len(headers)}' style='text-align:center;opacity:.7'>Aucune donnée</td></tr>"
    return f"""
<table class="table table-striped table-hover table-sm align-middle">
  <thead class="table-light"><tr>{thead}</tr></thead>
  <tbody>{tbody}</tbody>
</table>
""".strip()

def build_html(students, teachers, events) -> str:
    student_rows = [[
        s.get("student_id",""),
        s.get("full_name",""),
        s.get("email",""),
        s.get("phone",""),
        s.get("address",""),
        s.get("subscription_status",""),
        s.get("groupe",""),
        s.get("join_date","")
    ] for s in students]

    teacher_rows = [[
        t.get("teacher_id",""),
        t.get("full_name",""),
        t.get("email",""),
        t.get("phone",""),
        t.get("address",""),
        t.get("join_date","")
    ] for t in teachers]

    event_rows = [[
        e.get("event_name",""),
        e.get("event_date",""),
        ", ".join(e.get("organizers",[])),
        ", ".join(e.get("participants",[])),
        e.get("description","")
    ] for e in events]

    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>Madrassa — Tableau de bord</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
<style>
  body {{ background:#f7f8fb; }}
  .container {{ max-width: 1100px; }}
  .card {{ border-radius: 1rem; box-shadow: 0 6px 24px rgba(0,0,0,.06); }}
  h1,h2 {{ font-weight: 700; }}
  .badge-pill {{ border-radius: 999px; }}
</style>
</head>
<body>
<nav class="navbar navbar-expand-lg bg-body-tertiary border-bottom">
  <div class="container">
    <span class="navbar-brand fw-bold">Madrassa</span>
    <span class="badge text-bg-primary">Dashboard statique</span>
  </div>
</nav>

<main class="container py-4">
  <h1 class="mb-4">Tableau de bord</h1>

  <div class="row g-4">
    <div class="col-12">
      <div class="card">
        <div class="card-body">
          <h2 class="h4 mb-3">Événements</h2>
          {render_table(
            ["Nom", "Date", "Organisateurs", "Participants", "Description"],
            event_rows
          )}
        </div>
      </div>
    </div>

    <div class="col-12 col-lg-6">
      <div class="card">
        <div class="card-body">
          <h2 class="h4 mb-3">Étudiants</h2>
          {render_table(
            ["ID", "Nom", "Email", "Téléphone", "Adresse", "Abonnement", "Groupe", "Inscription"],
            student_rows
          )}
        </div>
      </div>
    </div>

    <div class="col-12 col-lg-6">
      <div class="card">
        <div class="card-body">
          <h2 class="h4 mb-3">Professeurs</h2>
          {render_table(
            ["ID", "Nom", "Email", "Téléphone", "Adresse", "Inscription"],
            teacher_rows
          )}
        </div>
      </div>
    </div>
  </div>
</main>

<footer class="py-4 text-center text-muted">
  Généré automatiquement depuis <code>data/members.json</code> et <code>data/events.json</code>.
</footer>
</body>
</html>
"""
    return html

class ReportGenerator:
    def __init__(self, base_dir: Path) -> None:
        self.base_dir = Path(base_dir)
        self.out_file = self.base_dir / "index.html"   # plus de dossier 'site'

    def build_and_save(self, members: List[Dict[str, Any]], events_raw: List[Dict[str, Any]]) -> Path:
        students, teachers = split_members(members)
        s_map, t_map = build_member_maps(students, teachers)
        events = parse_events(events_raw, s_map, t_map)
        html = build_html(students, teachers, events)
        self.out_file.write_text(html, encoding="utf-8")
        return self.out_file

    def open_in_browser(self, out_file: Path | None = None) -> None:
        target = out_file or self.out_file
        try:
            webbrowser.open(target.resolve().as_uri())
        except Exception as e:
            print(f"[WARN] Impossible d'ouvrir le navigateur: {e}")
