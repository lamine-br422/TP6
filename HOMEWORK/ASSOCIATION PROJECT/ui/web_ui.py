from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List, Tuple
from html import escape
import webbrowser

from interfaces.ui_interface import UIInterface


def _split_members(records: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    students: List[Dict[str, Any]] = []
    teachers: List[Dict[str, Any]] = []
    for r in records:
        item = dict(r)
        item.setdefault("full_name", item.get("name", ""))
        item.setdefault("email", "")
        item.setdefault("phone", "")
        item.setdefault("address", "")
        item.setdefault("join_date", "")
        if "student_id" in item:
            item.setdefault("subscription_status", "Pending")
            item.setdefault("groupe", "")
            item.setdefault("skills", [])
            item.setdefault("interests", [])
            students.append(item)
        elif "teacher_id" in item:
            item.setdefault("skills", [])
            item.setdefault("interests", [])
            teachers.append(item)
    return students, teachers


def _build_member_maps(
    students: List[Dict[str, Any]],
    teachers: List[Dict[str, Any]],
) -> Tuple[Dict[int, str], Dict[int, str]]:
    s_map: Dict[int, str] = {}
    t_map: Dict[int, str] = {}
    for s in students:
        sid = s.get("student_id")
        if sid is not None:
            try:
                s_map[int(sid)] = s.get("full_name", "")
            except ValueError:
                pass
    for t in teachers:
        tid = t.get("teacher_id")
        if tid is not None:
            try:
                t_map[int(tid)] = t.get("full_name", "")
            except ValueError:
                pass
    return s_map, t_map


def _parse_events(
    records: List[Dict[str, Any]],
    student_map: Dict[int, str],
    teacher_map: Dict[int, str],
) -> List[Dict[str, Any]]:
    parsed: List[Dict[str, Any]] = []
    for e in records:
        ev = dict(e)
        ev.setdefault("event_name", ev.get("name", ""))
        ev.setdefault("description", "")
        ev.setdefault("event_date", "")
        org_ids = ev.get("organizer_ids") or ev.get("organizers_ids") or []
        part_ids = ev.get("participant_ids") or ev.get("participants_ids") or []
        organizers: List[str] = []
        participants: List[str] = []
        for oid in org_ids:
            try:
                organizers.append(teacher_map.get(int(oid), f"Teacher#{oid}"))
            except ValueError:
                organizers.append(f"Teacher#{oid}")
        for sid in part_ids:
            try:
                participants.append(student_map.get(int(sid), f"Student#{sid}"))
            except ValueError:
                participants.append(f"Student#{sid}")
        parsed.append(
            {
                "event_name": ev["event_name"],
                "description": ev.get("description", ""),
                "event_date": ev.get("event_date", ""),
                "organizers": organizers,
                "participants": participants,
            }
        )
    return parsed


def _render_html(
    students: List[Dict[str, Any]],
    teachers: List[Dict[str, Any]],
    events: List[Dict[str, Any]],
    subs: List[Dict[str, Any]],
    donations: List[Dict[str, Any]],
) -> str:
    group_students: Dict[str, List[str]] = {}
    name_to_group: Dict[str, str] = {}
    for s in students:
        g = str(s.get("groupe", "") or "-")
        name = s.get("full_name", "")
        if not name:
            continue
        name_to_group[name] = g
        group_students.setdefault(g, []).append(name)

    id_to_name: Dict[int, str] = {}
    for s in students:
        sid = s.get("student_id")
        if sid is not None:
            try:
                id_to_name[int(sid)] = s.get("full_name", "")
            except ValueError:
                pass

    group_teachers: Dict[str, List[str]] = {}
    for e in events:
        orgs = e.get("organizers", [])
        parts = e.get("participants", [])
        for p in parts:
            g = name_to_group.get(p)
            if not g:
                continue
            for org in orgs:
                group_teachers.setdefault(g, [])
                if org not in group_teachers[g]:
                    group_teachers[g].append(org)

    style = """
    <style>
      :root{
        --bg-main:#050816;
        --bg-panel:#0b1220;
        --bg-header:#020617;
        --bg-table:#020617;
        --border:#1e293b;
        --accent:#38bdf8;
        --accent-soft:#0f172a;
        --text-main:#e5e7eb;
        --text-muted:#9ca3af;
        --danger:#f97373;
        --success:#4ade80;
      }
      *{box-sizing:border-box;margin:0;padding:0;}
      body{
        font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        background:var(--bg-main);
        color:var(--text-main);
      }
      header{
        background:var(--bg-header);
        border-bottom:1px solid var(--border);
        padding:12px 32px;
      }
      header h1{
        font-size:22px;
        font-weight:700;
      }
      .container{
        max-width:1200px;
        margin:24px auto 40px auto;
        padding:0 20px 40px 20px;
      }
      .subtitle{
        color:var(--text-muted);
        margin-top:8px;
        margin-bottom:24px;
      }
      .tabs-bar{
        display:flex;
        gap:8px;
        padding:12px 32px;
        background:var(--bg-header);
        border-bottom:1px solid var(--border);
        position:sticky;
        top:0;
        z-index:10;
      }
      .tab-btn{
        padding:6px 16px;
        border-radius:999px;
        border:1px solid transparent;
        background:transparent;
        color:var(--text-muted);
        font-size:14px;
        cursor:pointer;
        transition:all .15s ease;
      }
      .tab-btn:hover{
        border-color:var(--accent);
        color:var(--accent);
        background:rgba(56,189,248,0.08);
      }
      .tab-btn.active{
        background:var(--accent);
        color:#0f172a;
        border-color:var(--accent);
        font-weight:600;
      }
      .tab-section{
        display:none;
        margin-top:24px;
      }
      .tab-section.active{
        display:block;
      }
      h2{
        font-size:22px;
        font-weight:700;
        margin-bottom:12px;
      }
      table{
        width:100%;
        border-collapse:collapse;
        margin-top:12px;
        background:var(--bg-table);
        border-radius:12px;
        overflow:hidden;
        box-shadow:0 12px 30px rgba(15,23,42,0.8);
      }
      thead{
        background:#020617;
      }
      th,td{
        padding:10px 12px;
        font-size:13px;
        border-bottom:1px solid var(--border);
        white-space:nowrap;
      }
      th{
        text-align:left;
        color:var(--text-muted);
        font-weight:500;
      }
      tr:nth-child(even) td{
        background:#020617;
      }
      tr:hover td{
        background:#111827;
      }
      .badge{
        display:inline-block;
        font-size:11px;
        padding:2px 10px;
        border-radius:999px;
        border:1px solid transparent;
      }
      .badge-paid{
        color:#22c55e;
        border-color:#22c55e33;
        background:#16a34a1a;
      }
      .badge-pending{
        color:#eab308;
        border-color:#eab30833;
        background:#854d0e33;
      }
      .badge-unpaid{
        color:#f97373;
        border-color:#f9737333;
        background:#b91c1c33;
      }
      footer{
        text-align:center;
        color:var(--text-muted);
        font-size:12px;
        margin-top:32px;
        border-top:1px solid var(--border);
        padding-top:12px;
      }
      @media (max-width:900px){
        th,td{font-size:11px;padding:8px;}
        header, .tabs-bar{padding-inline:16px;}
        .container{padding-inline:12px;}
      }
    </style>
    """

    def esc(x: Any) -> str:
        return escape("" if x is None else str(x))

        stu_rows: List[str] = []
    for s in students:
        status = str(s.get("subscription_status", "Pending"))
        status_lower = status.lower()
        if status_lower == "paid":
            cls = "badge-paid"
        elif status_lower == "pending":
            cls = "badge-pending"
        else:
            cls = "badge-unpaid"
        stu_rows.append(
            "<tr>"
            f"<td>{esc(s.get('student_id',''))}</td>"
            f"<td>{esc(s.get('full_name',''))}</td>"
            f"<td>{esc(s.get('groupe',''))}</td>"  # <-- groupe affiché ici
            f"<td>{esc(s.get('email',''))}</td>"
            f"<td>{esc(s.get('phone',''))}</td>"
            f"<td>{esc(s.get('address',''))}</td>"
            f"<td>{esc(s.get('join_date',''))}</td>"
            f"<td>{esc(', '.join(s.get('skills',[])))}</td>"
            f"<td>{esc(', '.join(s.get('interests',[])))}</td>"
            f"<td><span class='badge {cls}'>{esc(status)}</span></td>"
            "</tr>"
        )


    tea_rows: List[str] = []
    for t in teachers:
        tea_rows.append(
            "<tr>"
            f"<td>{esc(t.get('teacher_id',''))}</td>"
            f"<td>{esc(t.get('full_name',''))}</td>"
            f"<td>{esc(t.get('email',''))}</td>"
            f"<td>{esc(t.get('phone',''))}</td>"
            f"<td>{esc(t.get('address',''))}</td>"
            f"<td>{esc(t.get('join_date',''))}</td>"
            f"<td>{esc(', '.join(t.get('skills',[])))}</td>"
            f"<td>{esc(', '.join(t.get('interests',[])))}</td>"
            "</tr>"
        )

    group_rows: List[str] = []
    for g, names in sorted(group_students.items(), key=lambda x: x[0]):
        teachers_for_group = ", ".join(group_teachers.get(g, [])) or "-"
        group_rows.append(
            "<tr>"
            f"<td>{esc(g)}</td>"
            f"<td>{esc(teachers_for_group)}</td>"
            f"<td>{esc(', '.join(names))}</td>"
            "</tr>"
        )

    evt_rows: List[str] = []
    for e in events:
        orgs = ", ".join(esc(n) for n in e.get("organizers", [])) or "-"
        parts = ", ".join(esc(n) for n in e.get("participants", [])) or "-"
        evt_rows.append(
            "<tr>"
            f"<td>{esc(e.get('event_name',''))}</td>"
            f"<td>{esc(e.get('description',''))}</td>"
            f"<td>{esc(e.get('event_date',''))}</td>"
            f"<td>{orgs}</td>"
            f"<td>{parts}</td>"
            "</tr>"
        )

    sub_rows: List[str] = []
    total_paid = 0.0
    total_unpaid = 0.0
    for sub in subs:
        sid = sub.get("student_id")
        try:
            sid_int = int(sid) if sid is not None else None
        except ValueError:
            sid_int = None
        student_name = id_to_name.get(sid_int, f"Student #{sid}") if sid_int is not None else "-"
        amount = float(sub.get("amount", 0.0))
        status = str(sub.get("status", "unpaid"))
        kind = str(sub.get("kind", "base")).lower()
        date_value = sub.get("date", "")
        if status.lower() == "paid":
            badge_cls = "badge-paid"
            total_paid += amount
        else:
            badge_cls = "badge-unpaid"
            total_unpaid += amount
        if kind == "monthly":
            kind_label = "Monthly"
        elif kind == "annual":
            kind_label = "Annual"
        else:
            kind_label = "Standard"
        sub_rows.append(
            "<tr>"
            f"<td>{esc(sid)}</td>"
            f"<td>{esc(student_name)}</td>"
            f"<td>{esc(kind_label)}</td>"
            f"<td>{amount:.2f}</td>"
            f"<td>{esc(date_value)}</td>"
            f"<td><span class='badge {badge_cls}'>{esc(status)}</span></td>"
            "</tr>"
        )

    don_rows: List[str] = []
    total_don = 0.0
    for d in donations:
        amount = float(d.get("amount", 0.0))
        total_don += amount
        don_rows.append(
            "<tr>"
            f"<td>{esc(d.get('donor_name',''))}</td>"
            f"<td>{esc(d.get('source',''))}</td>"
            f"<td>{amount:.2f}</td>"
            f"<td>{esc(d.get('date',''))}</td>"
            f"<td>{esc(d.get('purpose',''))}</td>"
            f"<td>{esc(d.get('note',''))}</td>"
            "</tr>"
        )

    html_doc: List[str] = [
        "<!doctype html>",
        "<html lang='fr'>",
        "<head>",
        "<meta charset='utf-8' />",
        "<title>Madrassa</title>",
        style,
        "<script>",
        "function showTab(name){",
        "  const sections=document.querySelectorAll('.tab-section');",
        "  sections.forEach(s=>s.classList.remove('active'));",
        "  const btns=document.querySelectorAll('.tab-btn');",
        "  btns.forEach(b=>b.classList.remove('active'));",
        "  const s=document.getElementById('tab-'+name);",
        "  const b=document.getElementById('btn-'+name);",
        "  if(s){s.classList.add('active');}",
        "  if(b){b.classList.add('active');}",
        "}",
        "document.addEventListener('DOMContentLoaded',()=>{showTab('students');});",
        "</script>",
        "</head>",
        "<body>",
        "<header>",
        "<h1>Madrassa</h1>",
        "</header>",
        "<div class='tabs-bar'>",
        "<button id='btn-students' class='tab-btn' onclick=\"showTab('students')\">Students</button>",
        "<button id='btn-teachers' class='tab-btn' onclick=\"showTab('teachers')\">Teachers</button>",
        "<button id='btn-groups' class='tab-btn' onclick=\"showTab('groups')\">Groups</button>",
        "<button id='btn-events' class='tab-btn' onclick=\"showTab('events')\">Events</button>",
        "<button id='btn-subscriptions' class='tab-btn' onclick=\"showTab('subscriptions')\">Subscriptions</button>",
        "<button id='btn-donations' class='tab-btn' onclick=\"showTab('donations')\">Donations</button>",
        "</div>",
        "<main class='container'>",
               "<section id='tab-students' class='tab-section'>",
        "<h2>Students</h2>",
        "<table>",
        "<thead><tr>",
        "<th>#</th><th>Full Name</th><th>Group</th><th>Email</th><th>Phone</th>",
        "<th>Address</th><th>Join Date</th><th>Skills</th><th>Interests</th><th>Subscription</th>",
        "</tr></thead>",
        "<tbody>",
        *(stu_rows if stu_rows else ["<tr><td colspan='10'>No students</td></tr>"]),

        "</tbody>",
        "</table>",
        "</section>",
        "<section id='tab-teachers' class='tab-section'>",
        "<h2>Teachers</h2>",
        "<table>",
        "<thead><tr>",
        "<th>#</th><th>Full Name</th><th>Email</th><th>Phone</th>",
        "<th>Address</th><th>Join Date</th><th>Skills</th><th>Interests</th>",
        "</tr></thead>",
        "<tbody>",
        *(tea_rows if tea_rows else ["<tr><td colspan='8'>No teachers</td></tr>"]),
        "</tbody>",
        "</table>",
        "</section>",
        "<section id='tab-groups' class='tab-section'>",
        "<h2>Groups</h2>",
        "<table>",
        "<thead><tr>",
        "<th>Group</th><th>Teacher</th><th>Students</th>",
        "</tr></thead>",
        "<tbody>",
        *(group_rows if group_rows else ["<tr><td colspan='3'>No groups</td></tr>"]),
        "</tbody>",
        "</table>",
        "</section>",
        "<section id='tab-events' class='tab-section'>",
        "<h2>Events</h2>",
        "<table>",
        "<thead><tr>",
        "<th>Name</th><th>Description</th><th>Date</th><th>Organizers</th><th>Participants</th>",
        "</tr></thead>",
        "<tbody>",
        *(evt_rows if evt_rows else ["<tr><td colspan='5'>No events</td></tr>"]),
        "</tbody>",
        "</table>",
        "</section>",
        "<section id='tab-subscriptions' class='tab-section'>",
        "<h2>Subscriptions</h2>",
        "<table>",
        "<thead><tr>",
        "<th>Student ID</th><th>Student</th><th>Type</th><th>Amount</th><th>Date</th><th>Status</th>",
        "</tr></thead>",
        "<tbody>",
        *(sub_rows if sub_rows else ["<tr><td colspan='6'>No subscriptions</td></tr>"]),
        "</tbody>",
        "</table>",
        f"<p style='margin-top:12px;font-size:13px;color:var(--text-muted);'>Total paid: {total_paid:.2f} | Total unpaid: {total_unpaid:.2f}</p>",
        "</section>",
        "<section id='tab-donations' class='tab-section'>",
        "<h2>Donations</h2>",
        "<table>",
        "<thead><tr>",
        "<th>Donor</th><th>Source</th><th>Amount</th><th>Date</th><th>Purpose</th><th>Note</th>",
        "</tr></thead>",
        "<tbody>",
        *(don_rows if don_rows else ["<tr><td colspan='6'>No donations</td></tr>"]),
        "</tbody>",
        "</table>",
        f"<p style='margin-top:12px;font-size:13px;color:var(--text-muted);'>Total donations: {total_don:.2f}</p>",
        "</section>",
        "</main>",
        "<footer>© 2026 Madrassa.</footer>",
        "</body>",
        "</html>",
    ]
    return "\n".join(html_doc)


class WebUI(UIInterface):
    def __init__(self, out_file: Path) -> None:
        self._out_file = out_file

    def show_dashboard(self, project: Dict[str, Any]) -> None:
        members = project.get("members", [])
        events_raw = project.get("events", [])
        subs = project.get("subscriptions", [])
        donations = project.get("donations", [])

        students, teachers = _split_members(members)
        s_map, t_map = _build_member_maps(students, teachers)
        events = _parse_events(events_raw, s_map, t_map)

        html = _render_html(students, teachers, events, subs, donations)

        self._out_file.parent.mkdir(parents=True, exist_ok=True)
        self._out_file.write_text(html, encoding="utf-8")
        try:
            webbrowser.open(self._out_file.resolve().as_uri())
        except Exception:
            pass
