from __future__ import annotations
from typing import Any, Dict, List, Tuple
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from interfaces.ui_interface import UIInterface
from views.web_view import _split_members, _build_member_maps, _parse_events
from observers.data_observer import Observer
from strategies.member_sorter import MemberSorter
from strategies.sort_by_id_strategy import SortByIdStrategy
from strategies.sort_by_date_strategy import SortByDateStrategy
from strategies.sort_by_group_strategy import SortByGroupStrategy
from strategies.sort_by_status_strategy import SortByStatusStrategy
from validators.field_validator import FieldValidator
from validators.form_configs import (
    get_student_field_definitions,
    get_teacher_field_definitions,
    get_event_field_definitions,
    get_donation_field_definitions,
    get_subscription_field_definitions,
)

# Couleurs du thème (identiques à la page web)
COLORS = {
    "bg_main": "#050816",
    "bg_panel": "#0b1220",
    "bg_header": "#020617",
    "bg_table": "#020617",
    "bg_table_alt": "#020617",
    "bg_table_hover": "#111827",
    "border": "#1e293b",
    "accent": "#38bdf8",
    "accent_soft": "#0f172a",
    "text_main": "#e5e7eb",
    "text_muted": "#9ca3af",
    "danger": "#f97373",
    "success": "#4ade80",
    "warning": "#eab308",
}


class GUIView(UIInterface, Observer):
    def __init__(self, controller=None) -> None:
        self.root = tk.Tk()
        self.root.title("Madrassa")
        self.root.configure(bg=COLORS["bg_main"])
        self.root.geometry("1200x700")

        self.controller = controller
        if controller:
            controller.attach_observer(self)

        self.current_tab = tk.StringVar(value="students")
        self.tab_frames: Dict[str, tk.Frame] = {}
        self.table_containers: Dict[str, tk.Widget] = {}

        self.students: List[Dict[str, Any]] = []
        self.teachers: List[Dict[str, Any]] = []
        self.events: List[Dict[str, Any]] = []
        self.subs: List[Dict[str, Any]] = []
        self.donations: List[Dict[str, Any]] = []
        
        # Variables pour le tri (pattern Strategy)
        self.students_sort_strategy = tk.StringVar(value="id")
        self.students_sort_reverse = tk.BooleanVar(value=False)
        self.teachers_sort_strategy = tk.StringVar(value="id")
        self.teachers_sort_reverse = tk.BooleanVar(value=False)
        
        # Instance de MemberSorter pour utiliser le pattern Strategy directement
        self._member_sorter = MemberSorter()

        self._setup_ui()

    def update(self, event_type: str, data: Any = None) -> None:
        if event_type.startswith("member_added_") or event_type.startswith("member_deleted_"):
            member_type = event_type.split("_")[-1]
            if member_type == "student":
                self._refresh_tab("students")
                self._refresh_tab("groups")
            elif member_type == "teacher":
                self._refresh_tab("teachers")
                self._refresh_tab("groups")
        elif event_type == "member_updated":
            self._refresh_tab("students")
            self._refresh_tab("groups")
        elif event_type == "event_added" or event_type == "event_deleted":
            self._refresh_tab("events")
            self._refresh_tab("groups")
        elif event_type == "subscription_added" or event_type == "subscription_deleted":
            self._refresh_tab("subscriptions")
        elif event_type == "donation_added" or event_type == "donation_deleted":
            self._refresh_tab("donations")

    # ------------------------------------------------------------------ UI de base

    def _setup_ui(self) -> None:
        """Configure l'interface utilisateur"""
        # Header
        header = tk.Frame(self.root, bg=COLORS["bg_header"], height=50)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)

        title = tk.Label(
            header,
            text="Madrassa",
            font=("Segoe UI", 22, "bold"),
            bg=COLORS["bg_header"],
            fg=COLORS["text_main"],
            anchor=tk.W,
            padx=32,
        )
        title.pack(side=tk.LEFT, fill=tk.Y)

        # Barre d'onglets
        tabs_frame = tk.Frame(self.root, bg=COLORS["bg_header"], height=45)
        tabs_frame.pack(fill=tk.X, side=tk.TOP)
        tabs_frame.pack_propagate(False)

        tabs_container = tk.Frame(tabs_frame, bg=COLORS["bg_header"])
        tabs_container.pack(side=tk.LEFT, padx=32, pady=8)

        self.tab_buttons: Dict[str, tk.Button] = {}
        tabs = ["students", "teachers", "groups", "events", "subscriptions", "donations"]
        tab_labels = ["Students", "Teachers", "Groups", "Events", "Subscriptions", "Donations"]

        for tab, label in zip(tabs, tab_labels):
            btn = tk.Button(
                tabs_container,
                text=label,
                font=("Segoe UI", 11),
                bg=COLORS["bg_header"],
                fg=COLORS["text_muted"],
                activebackground=COLORS["accent_soft"],
                activeforeground=COLORS["accent"],
                relief=tk.FLAT,
                borderwidth=1,
                padx=16,
                pady=6,
                cursor="hand2",
                command=lambda t=tab: self._switch_tab(t),
            )
            btn.pack(side=tk.LEFT, padx=2)
            self.tab_buttons[tab] = btn

        # Conteneur principal pour les onglets
        self.content_frame = tk.Frame(self.root, bg=COLORS["bg_main"])
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Créer les frames pour chaque onglet
        for tab in tabs:
            frame = tk.Frame(self.content_frame, bg=COLORS["bg_main"])
            self.tab_frames[tab] = frame

    def _switch_tab(self, tab_name: str) -> None:
        """Change l'onglet actif"""
        self.current_tab.set(tab_name)

        # Mettre à jour les boutons
        for name, btn in self.tab_buttons.items():
            if name == tab_name:
                btn.configure(
                    bg=COLORS["accent"],
                    fg="#0f172a",
                    font=("Segoe UI", 11, "bold"),
                )
            else:
                btn.configure(
                    bg=COLORS["bg_header"],
                    fg=COLORS["text_muted"],
                    font=("Segoe UI", 11),
                )

        # Afficher le bon frame
        for name, frame in self.tab_frames.items():
            if name == tab_name:
                frame.pack(fill=tk.BOTH, expand=True)
            else:
                frame.pack_forget()

    # ------------------------------------------------------------------ Table générique

    def _create_table(
        self,
        parent: tk.Widget,
        columns: List[Tuple[str, int]],
        data: List[List[str]],
    ) -> None:
        """Crée un tableau avec les données (colonnes alignées avec grid)."""
        table_container = tk.Frame(parent, bg=COLORS["bg_main"])
        table_container.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(
            table_container,
            bg=COLORS["bg_table"],
            highlightthickness=0,
            borderwidth=0,
        )
        scrollbar = ttk.Scrollbar(
            table_container,
            orient=tk.VERTICAL,
            command=canvas.yview,
        )
        scrollable_frame = tk.Frame(canvas, bg=COLORS["bg_table"])

        def configure_scroll_region(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))

        scrollable_frame.bind("<Configure>", configure_scroll_region)

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", tags="table_window")
        canvas.configure(yscrollcommand=scrollbar.set)

        def on_canvas_config(event):
            canvas.itemconfig("table_window", width=event.width)

        canvas.bind("<Configure>", on_canvas_config)

        for j in range(len(columns)):
            scrollable_frame.grid_columnconfigure(j, weight=1)

        # En-tête
        for col_index, (col_name, width) in enumerate(columns):
            lbl = tk.Label(
                scrollable_frame,
                text=col_name,
                font=("Segoe UI", 10, "bold"),
                bg=COLORS["bg_header"],
                fg=COLORS["text_muted"],
                anchor=tk.W,
                padx=12,
                pady=10,
                width=width,
            )
            lbl.grid(row=0, column=col_index, sticky="w")

        # Lignes
        for i, row_data in enumerate(data):
            base_bg = COLORS["bg_table_alt"] if i % 2 == 0 else COLORS["bg_table"]
            row_labels: List[tk.Label] = []

            for j, (col_name, width) in enumerate(columns):
                text = row_data[j] if j < len(row_data) else ""
                fg_color = COLORS["text_main"]
                if col_name.lower() in ("subscription", "status"):
                    status_lower = str(text).lower()
                    if status_lower == "paid":
                        fg_color = COLORS["success"]
                    elif status_lower == "pending":
                        fg_color = COLORS["warning"]
                    elif status_lower in ["unpaid", "overdue"]:
                        fg_color = COLORS["danger"]

                cell = tk.Label(
                    scrollable_frame,
                    text=text,
                    font=("Segoe UI", 10, "bold" if fg_color != COLORS["text_main"] else "normal"),
                    bg=base_bg,
                    fg=fg_color,
                    anchor=tk.W,
                    padx=12,
                    pady=8,
                    width=width,
                )
                cell.grid(row=i + 1, column=j, sticky="w")
                row_labels.append(cell)

            def on_enter(event, labels=row_labels):
                for lab in labels:
                    lab.configure(bg=COLORS["bg_table_hover"])

            def on_leave(event, labels=row_labels, bg=base_bg):
                for lab in labels:
                    lab.configure(bg=bg)

            for lab in row_labels:
                lab.bind("<Enter>", on_enter)
                lab.bind("<Leave>", on_leave)

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # ------------------------------------------------------------------ Badge (optionnel)

    def _create_badge(
        self,
        parent: tk.Widget,
        text: str,
        status: str,
    ) -> tk.Label:
        """Crée un badge de statut"""
        status_lower = status.lower()
        if status_lower == "paid":
            bg = "#16a34a1a"
            fg = COLORS["success"]
            border = "#22c55e33"
        elif status_lower == "pending":
            bg = "#854d0e33"
            fg = COLORS["warning"]
            border = "#eab30833"
        else:
            bg = "#b91c1c33"
            fg = COLORS["danger"]
            border = "#f9737333"

        badge = tk.Label(
            parent,
            text=text,
            font=("Segoe UI", 9),
            bg=bg,
            fg=fg,
            relief=tk.SOLID,
            borderwidth=1,
            padx=10,
            pady=2,
        )
        return badge

    # ------------------------------------------------------------------ Boutons Add/Delete/Refresh

    def _create_action_buttons(self, parent: tk.Widget, tab_name: str) -> tk.Frame:
        buttons_frame = tk.Frame(parent, bg=COLORS["bg_main"])
        buttons_frame.pack(fill=tk.X, pady=(0, 12))

        def create_button(text: str, command, color: str = COLORS["accent"]):
            btn = tk.Button(
                buttons_frame,
                text=text,
                font=("Segoe UI", 10, "bold"),
                bg=color,
                fg="#0f172a" if color in (COLORS["accent"], COLORS["success"]) else COLORS["text_main"],
                activebackground=COLORS["accent_soft"],
                activeforeground=COLORS["accent"],
                relief=tk.FLAT,
                padx=20,
                pady=8,
                cursor="hand2",
                command=command,
            )
            return btn

        add_btn = create_button("➕ Add", lambda: self._show_add_dialog(tab_name), COLORS["success"])
        add_btn.pack(side=tk.LEFT, padx=(0, 8))

        delete_btn = create_button("🗑️ Delete", lambda: self._show_delete_dialog(tab_name), COLORS["danger"])
        delete_btn.pack(side=tk.LEFT, padx=(0, 8))

        refresh_btn = create_button("🔄 Refresh", lambda: self._refresh_tab(tab_name), COLORS["accent"])
        refresh_btn.pack(side=tk.LEFT)

        return buttons_frame

    # ------------------------------------------------------------------ Gestion Groups (Add)

    def _add_group_assignment_dialog(self) -> None:
        """
        Affecter un étudiant ou un enseignant à un groupe.

        - Student : on met à jour le champ `groupe` dans members.json
        - Teacher : on crée un *event technique* dont le nom commence par
          "[GROUP_LINK]" pour lier Teacher ↔ Group (non affiché dans l’onglet Events)
        """
        if not self.controller:
            messagebox.showwarning("Warning", "Controller not available")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Add to Group")
        dialog.configure(bg=COLORS["bg_main"])
        dialog.geometry("450x280")
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(
            dialog,
            text="Type:",
            font=("Segoe UI", 10),
            bg=COLORS["bg_main"],
            fg=COLORS["text_main"],
        ).grid(row=0, column=0, sticky=tk.W, padx=20, pady=(20, 10))

        type_var = tk.StringVar(value="Student")
        ttk.Combobox(
            dialog,
            textvariable=type_var,
            values=["Student", "Teacher"],
            state="readonly",
            width=20,
        ).grid(row=0, column=1, padx=20, pady=(20, 10), sticky=tk.W)

        dynamic_frame = tk.Frame(dialog, bg=COLORS["bg_main"])
        dynamic_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=10, sticky=tk.W + tk.E)

        member_var = tk.StringVar()
        display_to_id: Dict[str, int] = {}

        def update_member_list(*args):
            nonlocal display_to_id
            for w in dynamic_frame.winfo_children():
                w.destroy()

            member_type = type_var.get()
            display_to_id.clear()

            if member_type == "Student":
                members = self.students or []
                id_key = "student_id"
                label_text = "Student:"
            else:
                members = self.teachers or []
                id_key = "teacher_id"
                label_text = "Teacher:"

            if not members:
                tk.Label(
                    dynamic_frame,
                    text=f"No {member_type.lower()}s available.",
                    font=("Segoe UI", 10),
                    bg=COLORS["bg_main"],
                    fg=COLORS["text_main"],
                ).pack()
                return

            for m in members:
                mid = m.get(id_key)
                name = m.get("full_name", f"{member_type} {mid}")
                if mid is None:
                    continue
                label = f"{mid} - {name}"
                display_to_id[label] = mid

            tk.Label(
                dynamic_frame,
                text=label_text,
                font=("Segoe UI", 10),
                bg=COLORS["bg_main"],
                fg=COLORS["text_main"],
            ).grid(row=0, column=0, sticky=tk.W, pady=(0, 10))

            combo = ttk.Combobox(
                dynamic_frame,
                textvariable=member_var,
                values=list(display_to_id.keys()),
                state="readonly",
                width=35,
            )
            combo.grid(row=0, column=1, sticky=tk.W, pady=(0, 10))
            if display_to_id:
                combo.current(0)

        type_var.trace("w", update_member_list)
        update_member_list()

        tk.Label(
            dialog,
            text="Group *:",
            font=("Segoe UI", 10),
            bg=COLORS["bg_main"],
            fg=COLORS["text_main"],
        ).grid(row=2, column=0, sticky=tk.W, padx=20, pady=10)

        group_entry = tk.Entry(dialog, font=("Segoe UI", 10), width=15)
        group_entry.grid(row=2, column=1, padx=20, pady=10, sticky=tk.W)

        def save():
            try:
                member_type = type_var.get()
                selected_label = member_var.get()

                if not selected_label or selected_label not in display_to_id:
                    if member_type == "Student":
                        messagebox.showerror("Erreur", "Veuillez sélectionner un étudiant")
                    else:
                        messagebox.showerror("Erreur", "Veuillez sélectionner un enseignant")
                    return

                member_id = display_to_id[selected_label]
                raw_group = group_entry.get().strip()

                if raw_group == "":
                    messagebox.showerror("Erreur", "Veuillez saisir le numéro du groupe")
                    return

                try:
                    group_val = int(raw_group)
                except ValueError:
                    messagebox.showerror("Erreur", "Le numéro du groupe doit être un nombre entier")
                    return

                if member_type == "Student":
                    # Validation : vérifier qu'il y a au moins un teacher dans ce groupe
                    import re
                    has_teacher = False
                    for e in self.events:
                        name = str(e.get("event_name", ""))
                        if name.startswith("[GROUP_LINK]"):
                            m = re.search(r"Group\s+(\d+)", name)
                            if m and int(m.group(1)) == group_val:
                                has_teacher = True
                                break
                    
                    if not has_teacher:
                        messagebox.showerror(
                            "Erreur",
                            f"Le groupe {group_val} n'existe pas.\n\n"
                            "Un groupe doit avoir au moins un enseignant avant d'ajouter des étudiants.\n"
                            "Veuillez d'abord ajouter un enseignant à ce groupe."
                        )
                        return
                    
                    ok = self.controller.get_member_controller().update_student_group(member_id, group_val)
                    if not ok:
                        messagebox.showerror("Erreur", "Étudiant non trouvé")
                        return
                    dialog.destroy()
                    messagebox.showinfo("Succès", f"L'étudiant a été ajouté au groupe {group_val} avec succès !")
                else:
                    # Teacher -> créer un event technique
                    from datetime import datetime

                    students_in_group: List[int] = []
                    for s in self.students:
                        if s.get("groupe") == group_val:
                            sid = s.get("student_id")
                            if sid is not None:
                                students_in_group.append(sid)

                    if not students_in_group:
                        # On autorise quand même, juste un warning
                        messagebox.showwarning(
                            "Warning",
                            f"No students in group {group_val}. "
                            "Teacher will still be linked to this group.",
                        )

                    teacher_name = selected_label.split(" - ", 1)[1] if " - " in selected_label else "Teacher"
                    event_name = f"[GROUP_LINK] {teacher_name} -> Group {group_val}"

                    event = {
                        "event_name": event_name,
                        "description": f"Technical link between {teacher_name} and group {group_val}",
                        "event_date": datetime.now().strftime("%Y-%m-%d"),
                        "organizer_ids": [member_id],
                        "participant_ids": students_in_group,
                    }

                    self.controller.get_event_controller().add_event(event)
                    dialog.destroy()
                    messagebox.showinfo("Succès", f"L'enseignant a été ajouté au groupe {group_val} avec succès !")

            except Exception as e:
                messagebox.showerror("Erreur", f"Échec de l'opération : {str(e)}")

        btn_frame = tk.Frame(dialog, bg=COLORS["bg_main"])
        btn_frame.grid(row=3, column=0, columnspan=2, pady=20)

        tk.Button(
            btn_frame,
            text="Save",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["success"],
            fg=COLORS["text_main"],
            padx=30,
            pady=8,
            command=save,
        ).pack(side=tk.LEFT, padx=10)

        tk.Button(
            btn_frame,
            text="Cancel",
            font=("Segoe UI", 10),
            bg=COLORS["bg_panel"],
            fg=COLORS["text_main"],
            padx=30,
            pady=8,
            command=dialog.destroy,
        ).pack(side=tk.LEFT, padx=10)

    # ------------------------------------------------------------------ Onglet Students

    def _populate_students_tab(self) -> None:
        frame = self.tab_frames["students"]
        for widget in frame.winfo_children():
            widget.destroy()

        # Titre
        title_frame = tk.Frame(frame, bg=COLORS["bg_main"])
        title_frame.pack(fill=tk.X, pady=(0, 12))
        
        title = tk.Label(
            title_frame,
            text="Students",
            font=("Segoe UI", 18, "bold"),
            bg=COLORS["bg_main"],
            fg=COLORS["text_main"],
            anchor=tk.W,
        )
        title.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Contrôles de tri (Pattern Strategy)
        sort_frame = tk.Frame(title_frame, bg=COLORS["bg_main"])
        sort_frame.pack(side=tk.RIGHT, padx=(10, 0))
        
        tk.Label(
            sort_frame,
            text="Trier par:",
            font=("Segoe UI", 10),
            bg=COLORS["bg_main"],
            fg=COLORS["text_muted"],
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        sort_combo = ttk.Combobox(
            sort_frame,
            textvariable=self.students_sort_strategy,
            values=["id", "date", "group", "status"],
            state="readonly",
            width=15,
            font=("Segoe UI", 10),
        )
        sort_combo.pack(side=tk.LEFT, padx=(0, 5))
        sort_combo.bind("<<ComboboxSelected>>", lambda e: self._apply_students_sort())
        
        reverse_check = tk.Checkbutton(
            sort_frame,
            text="Décroissant",
            variable=self.students_sort_reverse,
            font=("Segoe UI", 9),
            bg=COLORS["bg_main"],
            fg=COLORS["text_muted"],
            selectcolor=COLORS["bg_panel"],
            activebackground=COLORS["bg_main"],
            activeforeground=COLORS["text_main"],
            command=self._apply_students_sort,
        )
        reverse_check.pack(side=tk.LEFT, padx=(5, 0))
        
        # Désactiver la checkbox "Décroissant" quand le tri par date est sélectionné pour les students
        def on_students_sort_change(*args):
            if self.students_sort_strategy.get() == "date":
                reverse_check.config(state=tk.DISABLED)
                self.students_sort_reverse.set(False)  # Forcer à False pour ordre croissant
            else:
                reverse_check.config(state=tk.NORMAL)
            self._apply_students_sort()
        
        self.students_sort_strategy.trace("w", on_students_sort_change)

        self._create_action_buttons(frame, "students")
        
        # Trier les étudiants selon la stratégie choisie (Pattern Strategy)
        sorted_students = self._get_sorted_students()

        columns = [
            ("#", 5),
            ("Full Name", 20),
            ("Group", 8),
            ("Email", 25),
            ("Phone", 15),
            ("Address", 20),
            ("Join Date", 12),
            ("Skills", 20),
            ("Interests", 20),
            ("Subscription", 12),
        ]

        data = []
        for s in sorted_students:
            status = str(s.get("subscription_status", "Pending"))

            raw_group = s.get("groupe", "")
            if raw_group in (None, "", 0, "0"):
                group_display = "None"
            else:
                group_display = str(raw_group)

            row = [
                str(s.get("student_id", "")),
                str(s.get("full_name", "")),
                group_display,
                str(s.get("email", "")),
                str(s.get("phone", "")),
                str(s.get("address", "")),
                str(s.get("join_date", "")),
                ", ".join(s.get("skills", [])),
                ", ".join(s.get("interests", [])),
                status,
            ]
            data.append(row)

        if not data:
            tk.Label(
                frame,
                text="No students",
                font=("Segoe UI", 12),
                bg=COLORS["bg_main"],
                fg=COLORS["text_muted"],
            ).pack(pady=20)
        else:
            self._create_table(frame, columns, data)

    # ------------------------------------------------------------------ Onglet Teachers

    def _populate_teachers_tab(self) -> None:
        frame = self.tab_frames["teachers"]
        for widget in frame.winfo_children():
            widget.destroy()

        # Titre
        title_frame = tk.Frame(frame, bg=COLORS["bg_main"])
        title_frame.pack(fill=tk.X, pady=(0, 12))
        
        title = tk.Label(
            title_frame,
            text="Teachers",
            font=("Segoe UI", 18, "bold"),
            bg=COLORS["bg_main"],
            fg=COLORS["text_main"],
            anchor=tk.W,
        )
        title.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Contrôles de tri (Pattern Strategy)
        sort_frame = tk.Frame(title_frame, bg=COLORS["bg_main"])
        sort_frame.pack(side=tk.RIGHT, padx=(10, 0))
        
        tk.Label(
            sort_frame,
            text="Trier par:",
            font=("Segoe UI", 10),
            bg=COLORS["bg_main"],
            fg=COLORS["text_muted"],
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        sort_combo = ttk.Combobox(
            sort_frame,
            textvariable=self.teachers_sort_strategy,
            values=["id", "date"],
            state="readonly",
            width=15,
            font=("Segoe UI", 10),
        )
        sort_combo.pack(side=tk.LEFT, padx=(0, 5))
        sort_combo.bind("<<ComboboxSelected>>", lambda e: self._apply_teachers_sort())
        
        reverse_check = tk.Checkbutton(
            sort_frame,
            text="Décroissant",
            variable=self.teachers_sort_reverse,
            font=("Segoe UI", 9),
            bg=COLORS["bg_main"],
            fg=COLORS["text_muted"],
            selectcolor=COLORS["bg_panel"],
            activebackground=COLORS["bg_main"],
            activeforeground=COLORS["text_main"],
            command=self._apply_teachers_sort,
        )
        reverse_check.pack(side=tk.LEFT, padx=(5, 0))

        self._create_action_buttons(frame, "teachers")
        
        # Trier les professeurs selon la stratégie choisie (Pattern Strategy)
        sorted_teachers = self._get_sorted_teachers()

        columns = [
            ("#", 5),
            ("Full Name", 20),
            ("Email", 25),
            ("Phone", 15),
            ("Address", 20),
            ("Join Date", 12),
            ("Skills", 20),
            ("Interests", 20),
        ]

        data = []
        for t in sorted_teachers:
            row = [
                str(t.get("teacher_id", "")),
                str(t.get("full_name", "")),
                str(t.get("email", "")),
                str(t.get("phone", "")),
                str(t.get("address", "")),
                str(t.get("join_date", "")),
                ", ".join(t.get("skills", [])),
                ", ".join(t.get("interests", [])),
            ]
            data.append(row)

        if not data:
            tk.Label(
                frame,
                text="No teachers",
                font=("Segoe UI", 12),
                bg=COLORS["bg_main"],
                fg=COLORS["text_muted"],
            ).pack(pady=20)
        else:
            self._create_table(frame, columns, data)

    # ------------------------------------------------------------------ Onglet Groups

    def _populate_groups_tab(self) -> None:
        """
        Affiche les groupes.

        - Étudiants par groupe : champ `groupe`
        - Teachers par groupe : events dont le nom commence par "[GROUP_LINK]"
        - Un groupe est affiché même si aucun étudiant n'y est inscrit mais qu'un teacher est lié.
        """
        frame = self.tab_frames["groups"]
        for widget in frame.winfo_children():
            widget.destroy()

        title = tk.Label(
            frame,
            text="Groups",
            font=("Segoe UI", 18, "bold"),
            bg=COLORS["bg_main"],
            fg=COLORS["text_main"],
            anchor=tk.W,
        )
        title.pack(fill=tk.X, pady=(0, 12))

        self._create_action_buttons(frame, "groups")

        # Étudiants par groupe
        group_students: Dict[str, List[str]] = {}
        for s in self.students:
            g_raw = s.get("groupe")
            if g_raw in (None, "", 0):
                continue
            g = str(g_raw)
            name = s.get("full_name", "")
            if name:
                group_students.setdefault(g, []).append(name)

        # Teachers par groupe à partir des events techniques
        import re

        group_teachers: Dict[str, List[str]] = {}
        for e in self.events:
            name = str(e.get("event_name", ""))
            if not name.startswith("[GROUP_LINK]"):
                continue

            m = re.search(r"Group\s+(\d+)", name)
            if not m:
                continue
            gid = m.group(1)

            orgs = e.get("organizers", [])
            group_teachers.setdefault(gid, [])
            for org in orgs:
                if org not in group_teachers[gid]:
                    group_teachers[gid].append(org)

        # Ensemble de tous les groupes : ceux qui ont des students OU des teachers
        all_groups = set(group_students.keys()) | set(group_teachers.keys())

        columns = [
            ("Group", 10),
            ("Teacher", 30),
            ("Students", 50),
        ]

        data = []

        def _group_sort_key(key: str) -> tuple:
            try:
                return (0, int(key))
            except (TypeError, ValueError):
                return (1, key)

        for g in sorted(all_groups, key=_group_sort_key):
            teachers_for_group = ", ".join(group_teachers.get(g, [])) or "-"
            students_list = ", ".join(group_students.get(g, [])) or "-"
            data.append([g, teachers_for_group, students_list])

        if not data:
            tk.Label(
                frame,
                text="No groups",
                font=("Segoe UI", 12),
                bg=COLORS["bg_main"],
                fg=COLORS["text_muted"],
            ).pack(pady=20)
        else:
            self._create_table(frame, columns, data)

    # ------------------------------------------------------------------ Onglet Events

    def _populate_events_tab(self) -> None:
        """
        Affiche les événements.

        Les events techniques "[GROUP_LINK]" sont cachés pour ne pas polluer la liste.
        """
        frame = self.tab_frames["events"]
        for widget in frame.winfo_children():
            widget.destroy()

        title = tk.Label(
            frame,
            text="Events",
            font=("Segoe UI", 18, "bold"),
            bg=COLORS["bg_main"],
            fg=COLORS["text_main"],
            anchor=tk.W,
        )
        title.pack(fill=tk.X, pady=(0, 12))

        self._create_action_buttons(frame, "events")

        columns = [
            ("Name", 25),
            ("Description", 30),
            ("Date", 15),
            ("Organizers", 25),
            ("Participants", 30),
        ]

        data = []
        for e in self.events:
            name = str(e.get("event_name", ""))
            if name.startswith("[GROUP_LINK]"):
                continue  # on cache les events techniques

            orgs = ", ".join(e.get("organizers", [])) or "-"
            parts = ", ".join(e.get("participants", [])) or "-"
            row = [
                name,
                str(e.get("description", "")),
                str(e.get("event_date", "")),
                orgs,
                parts,
            ]
            data.append(row)

        if not data:
            tk.Label(
                frame,
                text="No events",
                font=("Segoe UI", 12),
                bg=COLORS["bg_main"],
                fg=COLORS["text_muted"],
            ).pack(pady=20)
        else:
            self._create_table(frame, columns, data)

    # ------------------------------------------------------------------ Onglet Subscriptions

    def _populate_subscriptions_tab(self) -> None:
        frame = self.tab_frames["subscriptions"]
        for widget in frame.winfo_children():
            widget.destroy()

        title = tk.Label(
            frame,
            text="Subscriptions",
            font=("Segoe UI", 18, "bold"),
            bg=COLORS["bg_main"],
            fg=COLORS["text_main"],
            anchor=tk.W,
        )
        title.pack(fill=tk.X, pady=(0, 12))

        self._create_action_buttons(frame, "subscriptions")

        id_to_name: Dict[int, str] = {}
        for s in self.students:
            sid = s.get("student_id")
            if sid is not None:
                try:
                    id_to_name[int(sid)] = s.get("full_name", "")
                except ValueError:
                    pass

        columns = [
            ("Student ID", 10),
            ("Student", 25),
            ("Type", 12),
            ("Amount", 12),
            ("Date", 15),
            ("Status", 12),
        ]

        data = []
        total_paid = 0.0
        total_unpaid = 0.0

        for sub in self.subs:
            sid = sub.get("student_id")
            try:
                sid_int = int(sid) if sid is not None else None
            except ValueError:
                sid_int = None
            student_name = id_to_name.get(sid_int, f"Student #{sid}") if sid_int is not None else "-"
            amount = float(sub.get("amount", 0.0))
            status = str(sub.get("status", "unpaid"))
            kind = str(sub.get("kind", "base")).lower()

            if status.lower() == "paid":
                total_paid += amount
            else:
                total_unpaid += amount

            if kind == "monthly":
                kind_label = "Monthly"
            elif kind == "annual":
                kind_label = "Annual"
            else:
                kind_label = "Standard"

            row = [
                str(sid),
                student_name,
                kind_label,
                f"{amount:.2f}",
                str(sub.get("date", "")),
                status,
            ]
            data.append(row)

        if not data:
            tk.Label(
                frame,
                text="No subscriptions",
                font=("Segoe UI", 12),
                bg=COLORS["bg_main"],
                fg=COLORS["text_muted"],
            ).pack(pady=20)
        else:
            self._create_table(frame, columns, data)

            totals_frame = tk.Frame(frame, bg=COLORS["bg_main"])
            totals_frame.pack(fill=tk.X, pady=(12, 0))

            totals_text = f"Total paid: {total_paid:.2f} | Total unpaid: {total_unpaid:.2f}"
            tk.Label(
                totals_frame,
                text=totals_text,
                font=("Segoe UI", 10),
                bg=COLORS["bg_main"],
                fg=COLORS["text_muted"],
                anchor=tk.W,
            ).pack()

    # ------------------------------------------------------------------ Onglet Donations

    def _populate_donations_tab(self) -> None:
        frame = self.tab_frames["donations"]
        for widget in frame.winfo_children():
            widget.destroy()

        title = tk.Label(
            frame,
            text="Donations",
            font=("Segoe UI", 18, "bold"),
            bg=COLORS["bg_main"],
            fg=COLORS["text_main"],
            anchor=tk.W,
        )
        title.pack(fill=tk.X, pady=(0, 12))

        self._create_action_buttons(frame, "donations")

        columns = [
            ("Donor", 20),
            ("Source", 20),
            ("Amount", 15),
            ("Date", 15),
            ("Purpose", 25),
            ("Note", 30),
        ]

        data = []
        total_don = 0.0

        for d in self.donations:
            amount = float(d.get("amount", 0.0))
            total_don += amount
            row = [
                str(d.get("donor_name", "")),
                str(d.get("source", "")),
                f"{amount:.2f}",
                str(d.get("date", "")),
                str(d.get("purpose", "")),
                str(d.get("note", "")),
            ]
            data.append(row)

        if not data:
            tk.Label(
                frame,
                text="No donations",
                font=("Segoe UI", 12),
                bg=COLORS["bg_main"],
                fg=COLORS["text_muted"],
            ).pack(pady=20)
        else:
            self._create_table(frame, columns, data)

            totals_frame = tk.Frame(frame, bg=COLORS["bg_main"])
            totals_frame.pack(fill=tk.X, pady=(12, 0))

            totals_text = f"Total donations: {total_don:.2f}"
            tk.Label(
                totals_frame,
                text=totals_text,
                font=("Segoe UI", 10),
                bg=COLORS["bg_main"],
                fg=COLORS["text_muted"],
                anchor=tk.W,
            ).pack()

    # ------------------------------------------------------------------ Refresh onglets

    # ------------------------------------------------------------------ Méthodes de tri (Pattern Strategy)
    
    def _get_sorted_students(self) -> List[Dict[str, Any]]:
        """
        Trie les étudiants selon la stratégie choisie en utilisant le pattern Strategy.
        
        Utilise directement self.students pour garantir la cohérence avec les données affichées.
        
        Returns:
            Liste des étudiants triés
        """
        if not self.students:
            return self.students
        
        try:
            sort_by = self.students_sort_strategy.get()
            reverse = self.students_sort_reverse.get()
            
            # Pour le tri par date des students, toujours en ordre croissant (plus ancien d'abord)
            if sort_by == "date":
                reverse = False
            
            # Sélectionner la stratégie appropriée
            strategy_map = {
                "id": SortByIdStrategy(),
                "date": SortByDateStrategy(),
                "group": SortByGroupStrategy(),
                "status": SortByStatusStrategy(),
            }
            
            strategy = strategy_map.get(sort_by.lower(), SortByIdStrategy())
            self._member_sorter.set_strategy(strategy)
            
            # Trier directement les données affichées (self.students)
            return self._member_sorter.sort(self.students.copy(), reverse)
        except Exception as e:
            # En cas d'erreur, retourner la liste non triée
            print(f"Erreur lors du tri des students: {e}")
            return self.students
    
    def _get_sorted_teachers(self) -> List[Dict[str, Any]]:
        """
        Trie les professeurs selon la stratégie choisie en utilisant le pattern Strategy.
        
        Utilise directement self.teachers pour garantir la cohérence avec les données affichées.
        
        Returns:
            Liste des professeurs triés
        """
        if not self.teachers:
            return self.teachers
        
        try:
            sort_by = self.teachers_sort_strategy.get()
            reverse = self.teachers_sort_reverse.get()
            
            # Pour les teachers, seules les stratégies "id" et "date" sont valides
            if sort_by not in ["id", "date"]:
                sort_by = "id"
            
            # Sélectionner la stratégie appropriée
            strategy_map = {
                "id": SortByIdStrategy(),
                "date": SortByDateStrategy(),
            }
            
            strategy = strategy_map.get(sort_by.lower(), SortByIdStrategy())
            self._member_sorter.set_strategy(strategy)
            
            # Trier directement les données affichées (self.teachers)
            return self._member_sorter.sort(self.teachers.copy(), reverse)
        except Exception as e:
            # En cas d'erreur, retourner la liste non triée
            print(f"Erreur lors du tri des teachers: {e}")
            return self.teachers
    
    def _apply_students_sort(self) -> None:
        """Applique le tri aux étudiants et rafraîchit l'affichage"""
        if self.current_tab.get() == "students":
            self._populate_students_tab()
    
    def _apply_teachers_sort(self) -> None:
        """Applique le tri aux professeurs et rafraîchit l'affichage"""
        if self.current_tab.get() == "teachers":
            self._populate_teachers_tab()

    def _refresh_tab(self, tab_name: str) -> None:
        if not self.controller:
            return

        project = self.controller.get_dashboard_data()
        members = project.get("members", [])
        events_raw = project.get("events", [])
        subs = project.get("subscriptions", [])
        donations = project.get("donations", [])

        self.students, self.teachers = _split_members(members)
        s_map, t_map = _build_member_maps(self.students, self.teachers)
        self.events = _parse_events(events_raw, s_map, t_map)
        self.subs = subs
        self.donations = donations

        if tab_name == "students":
            self._populate_students_tab()
        elif tab_name == "teachers":
            self._populate_teachers_tab()
        elif tab_name == "groups":
            self._populate_groups_tab()
        elif tab_name == "events":
            self._populate_events_tab()
        elif tab_name == "subscriptions":
            self._populate_subscriptions_tab()
        elif tab_name == "donations":
            self._populate_donations_tab()

    # ------------------------------------------------------------------ Dialogues ADD

    def _show_add_dialog(self, tab_name: str) -> None:
        if not self.controller:
            messagebox.showwarning("Warning", "Controller not available")
            return

        if tab_name == "students":
            self._add_student_dialog()
        elif tab_name == "teachers":
            self._add_teacher_dialog()
        elif tab_name == "events":
            self._add_event_dialog()
        elif tab_name == "subscriptions":
            self._add_subscription_dialog()
        elif tab_name == "donations":
            self._add_donation_dialog()
        elif tab_name == "groups":
            self._add_group_assignment_dialog()

    def _add_student_dialog(self) -> None:
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Student")
        dialog.configure(bg=COLORS["bg_main"])
        dialog.geometry("750x650")
        dialog.transient(self.root)
        dialog.grab_set()

        # Configuration de validation
        field_definitions = get_student_field_definitions()
        validator = FieldValidator(field_definitions)
        fields = {}
        error_labels = {}

        # Créer les champs avec labels et indicateurs *
        for i, field_def in enumerate(field_definitions):
            label_text = field_def.get_label_with_asterisk()
            tk.Label(
                dialog,
                text=label_text + ":",
                font=("Segoe UI", 10),
                bg=COLORS["bg_main"],
                fg=COLORS["text_main"],
            ).grid(row=i, column=0, sticky=tk.W, padx=20, pady=10)

            entry = tk.Entry(dialog, font=("Segoe UI", 10), width=40)
            entry.grid(row=i, column=1, padx=20, pady=10)
            fields[field_def.name] = entry

            # Label pour afficher les erreurs
            error_label = tk.Label(
                dialog,
                text="",
                font=("Segoe UI", 8),
                bg=COLORS["bg_main"],
                fg=COLORS["danger"],
                wraplength=200,
                justify=tk.LEFT,
            )
            error_label.grid(row=i, column=2, sticky=tk.W, padx=5)
            error_labels[field_def.name] = error_label

        def save():
            # Effacer toutes les erreurs précédentes
            for error_label in error_labels.values():
                error_label.config(text="")
            
            # Collecter les valeurs
            field_values = {name: entry.get() for name, entry in fields.items()}
            
            # Valider
            errors = validator.get_errors(field_values)
            
            # Afficher les erreurs dans les labels
            for field_name, error_label in error_labels.items():
                if field_name in errors:
                    error_label.config(text=errors[field_name])
                else:
                    error_label.config(text="")
            
            # Si des erreurs existent, ne pas continuer mais ne pas afficher de messagebox
            # Les erreurs sont déjà visibles dans les labels
            if errors:
                return

            try:
                student_id = self.controller.get_member_controller().get_next_student_id()
                skills = [s.strip() for s in fields["skills"].get().split(",") if s.strip()]
                interests = [i.strip() for i in fields["interests"].get().split(",") if i.strip()]

                student = self.controller.get_member_controller().create_student(
                    student_id=student_id,
                    full_name=fields["full_name"].get(),
                    email=fields["email"].get(),
                    phone=fields["phone"].get(),
                    address=fields["address"].get(),
                    join_date=fields["join_date"].get(),
                    subscription_status=fields["subscription_status"].get() or "Pending",
                    groupe=None,
                    skills=skills,
                    interests=interests,
                )

                self.controller.get_member_controller().add_member(student)
                dialog.destroy()
                messagebox.showinfo("Success", "Student added successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add student: {str(e)}")

        btn_frame = tk.Frame(dialog, bg=COLORS["bg_main"])
        btn_frame.grid(row=len(field_definitions), column=0, columnspan=3, pady=20)

        tk.Button(
            btn_frame,
            text="Save",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["success"],
            fg=COLORS["text_main"],
            padx=30,
            pady=8,
            command=save,
        ).pack(side=tk.LEFT, padx=10)

        tk.Button(
            btn_frame,
            text="Cancel",
            font=("Segoe UI", 10),
            bg=COLORS["bg_panel"],
            fg=COLORS["text_main"],
            padx=30,
            pady=8,
            command=dialog.destroy,
        ).pack(side=tk.LEFT, padx=10)

    def _add_teacher_dialog(self) -> None:
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Teacher")
        dialog.configure(bg=COLORS["bg_main"])
        dialog.geometry("750x600")
        dialog.transient(self.root)
        dialog.grab_set()

        # Configuration de validation
        field_definitions = get_teacher_field_definitions()
        validator = FieldValidator(field_definitions)
        fields = {}
        error_labels = {}

        # Créer les champs avec labels et indicateurs *
        for i, field_def in enumerate(field_definitions):
            label_text = field_def.get_label_with_asterisk()
            tk.Label(
                dialog,
                text=label_text + ":",
                font=("Segoe UI", 10),
                bg=COLORS["bg_main"],
                fg=COLORS["text_main"],
            ).grid(row=i, column=0, sticky=tk.W, padx=20, pady=10)

            entry = tk.Entry(dialog, font=("Segoe UI", 10), width=40)
            entry.grid(row=i, column=1, padx=20, pady=10)
            fields[field_def.name] = entry

            # Label pour afficher les erreurs
            error_label = tk.Label(
                dialog,
                text="",
                font=("Segoe UI", 8),
                bg=COLORS["bg_main"],
                fg=COLORS["danger"],
                wraplength=200,
                justify=tk.LEFT,
            )
            error_label.grid(row=i, column=2, sticky=tk.W, padx=5)
            error_labels[field_def.name] = error_label

        def save():
            # Effacer toutes les erreurs précédentes
            for error_label in error_labels.values():
                error_label.config(text="")
            
            # Collecter les valeurs
            field_values = {name: entry.get() for name, entry in fields.items()}
            
            # Valider
            errors = validator.get_errors(field_values)
            
            # Afficher les erreurs dans les labels
            for field_name, error_label in error_labels.items():
                if field_name in errors:
                    error_label.config(text=errors[field_name])
                else:
                    error_label.config(text="")
            
            # Si des erreurs existent, ne pas continuer mais ne pas afficher de messagebox
            # Les erreurs sont déjà visibles dans les labels
            if errors:
                return

            try:
                teacher_id = self.controller.get_member_controller().get_next_teacher_id()
                skills = [s.strip() for s in fields["skills"].get().split(",") if s.strip()]
                interests = [i.strip() for i in fields["interests"].get().split(",") if i.strip()]

                teacher = self.controller.get_member_controller().create_teacher(
                    teacher_id=teacher_id,
                    full_name=fields["full_name"].get(),
                    email=fields["email"].get(),
                    phone=fields["phone"].get(),
                    address=fields["address"].get(),
                    join_date=fields["join_date"].get(),
                    skills=skills,
                    interests=interests,
                )

                self.controller.get_member_controller().add_member(teacher)
                dialog.destroy()
                messagebox.showinfo("Success", "Teacher added successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add teacher: {str(e)}")

        btn_frame = tk.Frame(dialog, bg=COLORS["bg_main"])
        btn_frame.grid(row=len(field_definitions), column=0, columnspan=3, pady=20)

        tk.Button(
            btn_frame,
            text="Save",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["success"],
            fg=COLORS["text_main"],
            padx=30,
            pady=8,
            command=save,
        ).pack(side=tk.LEFT, padx=10)

        tk.Button(
            btn_frame,
            text="Cancel",
            font=("Segoe UI", 10),
            bg=COLORS["bg_panel"],
            fg=COLORS["text_main"],
            padx=30,
            pady=8,
            command=dialog.destroy,
        ).pack(side=tk.LEFT, padx=10)

    def _add_event_dialog(self) -> None:
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Event")
        dialog.configure(bg=COLORS["bg_main"])
        dialog.geometry("750x500")
        dialog.transient(self.root)
        dialog.grab_set()

        # Configuration de validation
        field_definitions = get_event_field_definitions()
        validator = FieldValidator(field_definitions)
        fields = {}
        error_labels = {}

        # Créer les champs avec labels et indicateurs *
        for i, field_def in enumerate(field_definitions):
            label_text = field_def.get_label_with_asterisk()
            tk.Label(
                dialog,
                text=label_text + ":",
                font=("Segoe UI", 10),
                bg=COLORS["bg_main"],
                fg=COLORS["text_main"],
            ).grid(row=i, column=0, sticky=tk.W, padx=20, pady=10)

            entry = tk.Entry(dialog, font=("Segoe UI", 10), width=40)
            entry.grid(row=i, column=1, padx=20, pady=10)
            fields[field_def.name] = entry

            # Label pour afficher les erreurs
            error_label = tk.Label(
                dialog,
                text="",
                font=("Segoe UI", 8),
                bg=COLORS["bg_main"],
                fg=COLORS["danger"],
                wraplength=200,
                justify=tk.LEFT,
            )
            error_label.grid(row=i, column=2, sticky=tk.W, padx=5)
            error_labels[field_def.name] = error_label

        def save():
            # Effacer toutes les erreurs précédentes
            for error_label in error_labels.values():
                error_label.config(text="")
            
            # Collecter les valeurs
            field_values = {name: entry.get() for name, entry in fields.items()}
            
            # Valider
            errors = validator.get_errors(field_values)
            
            # Afficher les erreurs dans les labels
            for field_name, error_label in error_labels.items():
                if field_name in errors:
                    error_label.config(text=errors[field_name])
                else:
                    error_label.config(text="")
            
            # Si des erreurs existent, ne pas continuer mais ne pas afficher de messagebox
            # Les erreurs sont déjà visibles dans les labels
            if errors:
                return

            try:
                org_ids = [int(x.strip()) for x in fields["organizer_ids"].get().split(",") if x.strip()]
                part_ids = [int(x.strip()) for x in fields["participant_ids"].get().split(",") if x.strip()]

                event = {
                    "event_name": fields["event_name"].get(),
                    "description": fields["description"].get(),
                    "event_date": fields["event_date"].get(),
                    "organizer_ids": org_ids,
                    "participant_ids": part_ids,
                }

                self.controller.get_event_controller().add_event(event)
                dialog.destroy()
                messagebox.showinfo("Success", "Event added successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add event: {str(e)}")

        btn_frame = tk.Frame(dialog, bg=COLORS["bg_main"])
        btn_frame.grid(row=len(field_definitions), column=0, columnspan=3, pady=20)

        tk.Button(
            btn_frame,
            text="Save",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["success"],
            fg=COLORS["text_main"],
            padx=30,
            pady=8,
            command=save,
        ).pack(side=tk.LEFT, padx=10)

        tk.Button(
            btn_frame,
            text="Cancel",
            font=("Segoe UI", 10),
            bg=COLORS["bg_panel"],
            fg=COLORS["text_main"],
            padx=30,
            pady=8,
            command=dialog.destroy,
        ).pack(side=tk.LEFT, padx=10)

    def _add_subscription_dialog(self) -> None:
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Subscription")
        dialog.configure(bg=COLORS["bg_main"])
        dialog.geometry("750x450")
        dialog.transient(self.root)
        dialog.grab_set()

        # Configuration de validation
        field_definitions = get_subscription_field_definitions()
        validator = FieldValidator(field_definitions)
        fields = {}
        error_labels = {}

        # Créer les champs avec labels et indicateurs *
        for i, field_def in enumerate(field_definitions):
            label_text = field_def.get_label_with_asterisk()
            tk.Label(
                dialog,
                text=label_text + ":",
                font=("Segoe UI", 10),
                bg=COLORS["bg_main"],
                fg=COLORS["text_main"],
            ).grid(row=i, column=0, sticky=tk.W, padx=20, pady=10)

            entry = tk.Entry(dialog, font=("Segoe UI", 10), width=40)
            entry.grid(row=i, column=1, padx=20, pady=10)
            fields[field_def.name] = entry

            # Label pour afficher les erreurs
            error_label = tk.Label(
                dialog,
                text="",
                font=("Segoe UI", 8),
                bg=COLORS["bg_main"],
                fg=COLORS["danger"],
                wraplength=200,
                justify=tk.LEFT,
            )
            error_label.grid(row=i, column=2, sticky=tk.W, padx=5)
            error_labels[field_def.name] = error_label

        def save():
            # Effacer toutes les erreurs précédentes
            for error_label in error_labels.values():
                error_label.config(text="")
            
            # Collecter les valeurs
            field_values = {name: entry.get() for name, entry in fields.items()}
            
            # Valider
            errors = validator.get_errors(field_values)
            
            # Afficher les erreurs dans les labels
            for field_name, error_label in error_labels.items():
                if field_name in errors:
                    error_label.config(text=errors[field_name])
                else:
                    error_label.config(text="")
            
            # Si des erreurs existent, ne pas continuer mais ne pas afficher de messagebox
            # Les erreurs sont déjà visibles dans les labels
            if errors:
                return

            try:
                subscription = {
                    "student_id": int(fields["student_id"].get()),
                    "amount": float(fields["amount"].get()),
                    "date": fields["date"].get(),
                    "status": fields["status"].get() or "unpaid",
                    "kind": fields["kind"].get() or "base",
                }
                if subscription["kind"] == "monthly":
                    subscription["months"] = 1

                self.controller.get_finance_controller().add_subscription(subscription)
                dialog.destroy()
                messagebox.showinfo("Success", "Subscription added successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add subscription: {str(e)}")

        btn_frame = tk.Frame(dialog, bg=COLORS["bg_main"])
        btn_frame.grid(row=len(field_definitions), column=0, columnspan=3, pady=20)

        tk.Button(
            btn_frame,
            text="Save",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["success"],
            fg=COLORS["text_main"],
            padx=30,
            pady=8,
            command=save,
        ).pack(side=tk.LEFT, padx=10)

        tk.Button(
            btn_frame,
            text="Cancel",
            font=("Segoe UI", 10),
            bg=COLORS["bg_panel"],
            fg=COLORS["text_main"],
            padx=30,
            pady=8,
            command=dialog.destroy,
        ).pack(side=tk.LEFT, padx=10)

    def _add_donation_dialog(self) -> None:
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Donation")
        dialog.configure(bg=COLORS["bg_main"])
        dialog.geometry("750x500")
        dialog.transient(self.root)
        dialog.grab_set()

        # Configuration de validation
        field_definitions = get_donation_field_definitions()
        validator = FieldValidator(field_definitions)
        fields = {}
        error_labels = {}

        # Créer les champs avec labels et indicateurs *
        for i, field_def in enumerate(field_definitions):
            label_text = field_def.get_label_with_asterisk()
            tk.Label(
                dialog,
                text=label_text + ":",
                font=("Segoe UI", 10),
                bg=COLORS["bg_main"],
                fg=COLORS["text_main"],
            ).grid(row=i, column=0, sticky=tk.W, padx=20, pady=10)

            entry = tk.Entry(dialog, font=("Segoe UI", 10), width=40)
            entry.grid(row=i, column=1, padx=20, pady=10)
            fields[field_def.name] = entry

            # Label pour afficher les erreurs
            error_label = tk.Label(
                dialog,
                text="",
                font=("Segoe UI", 8),
                bg=COLORS["bg_main"],
                fg=COLORS["danger"],
                wraplength=200,
                justify=tk.LEFT,
            )
            error_label.grid(row=i, column=2, sticky=tk.W, padx=5)
            error_labels[field_def.name] = error_label

        def save():
            # Effacer toutes les erreurs précédentes
            for error_label in error_labels.values():
                error_label.config(text="")
            
            # Collecter les valeurs
            field_values = {name: entry.get() for name, entry in fields.items()}
            
            # Valider
            errors = validator.get_errors(field_values)
            
            # Afficher les erreurs dans les labels
            for field_name, error_label in error_labels.items():
                if field_name in errors:
                    error_label.config(text=errors[field_name])
                else:
                    error_label.config(text="")
            
            # Si des erreurs existent, ne pas continuer mais ne pas afficher de messagebox
            # Les erreurs sont déjà visibles dans les labels
            if errors:
                return

            try:
                donation = {
                    "donor_name": fields["donor_name"].get(),
                    "source": fields["source"].get(),
                    "amount": float(fields["amount"].get()),
                    "date": fields["date"].get(),
                    "purpose": fields["purpose"].get(),
                    "note": fields["note"].get(),
                }

                self.controller.get_finance_controller().add_donation(donation)
                dialog.destroy()
                messagebox.showinfo("Success", "Donation added successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add donation: {str(e)}")

        btn_frame = tk.Frame(dialog, bg=COLORS["bg_main"])
        btn_frame.grid(row=len(field_definitions), column=0, columnspan=3, pady=20)

        tk.Button(
            btn_frame,
            text="Save",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["success"],
            fg=COLORS["text_main"],
            padx=30,
            pady=8,
            command=save,
        ).pack(side=tk.LEFT, padx=10)

        tk.Button(
            btn_frame,
            text="Cancel",
            font=("Segoe UI", 10),
            bg=COLORS["bg_panel"],
            fg=COLORS["text_main"],
            padx=30,
            pady=8,
            command=dialog.destroy,
        ).pack(side=tk.LEFT, padx=10)

    # ------------------------------------------------------------------ Dialogues DELETE

    def _show_delete_dialog(self, tab_name: str) -> None:
        if not self.controller:
            messagebox.showwarning("Warning", "Controller not available")
            return

        if tab_name == "students":
            self._delete_student_dialog()
        elif tab_name == "teachers":
            self._delete_teacher_dialog()
        elif tab_name == "events":
            self._delete_event_dialog()
        elif tab_name == "subscriptions":
            self._delete_subscription_dialog()
        elif tab_name == "donations":
            self._delete_donation_dialog()
        elif tab_name == "groups":
            self._delete_from_group_dialog()

    def _delete_student_dialog(self) -> None:
        student_id = simpledialog.askinteger("Delete Student", "Enter Student ID:")
        if student_id is not None:
            if self.controller.get_member_controller().delete_member(student_id, "student"):
                messagebox.showinfo("Success", "Student deleted successfully!")
            else:
                messagebox.showerror("Error", "Student not found!")

    def _delete_teacher_dialog(self) -> None:
        teacher_id = simpledialog.askinteger("Delete Teacher", "Enter Teacher ID:")
        if teacher_id is not None:
            if self.controller.get_member_controller().delete_member(teacher_id, "teacher"):
                messagebox.showinfo("Success", "Teacher deleted successfully!")
            else:
                messagebox.showerror("Error", "Teacher not found!")

    def _delete_from_group_dialog(self) -> None:
        """
        Supprimer un étudiant ou un enseignant d'un groupe.

        - Student : on met groupe = None
        - Teacher : on supprime l'event technique "[GROUP_LINK] {teacher} -> Group {g}"
          (sans popup de confirmation supplémentaire).
        """
        if not self.controller:
            messagebox.showwarning("Warning", "Controller not available")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Remove from Group")
        dialog.configure(bg=COLORS["bg_main"])
        dialog.geometry("450x280")
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(
            dialog,
            text="Type:",
            font=("Segoe UI", 10),
            bg=COLORS["bg_main"],
            fg=COLORS["text_main"],
        ).grid(row=0, column=0, sticky=tk.W, padx=20, pady=(20, 10))

        type_var = tk.StringVar(value="Student")
        ttk.Combobox(
            dialog,
            textvariable=type_var,
            values=["Student", "Teacher"],
            state="readonly",
            width=20,
        ).grid(row=0, column=1, padx=20, pady=(20, 10), sticky=tk.W)

        dynamic_frame = tk.Frame(dialog, bg=COLORS["bg_main"])
        dynamic_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=10, sticky=tk.W + tk.E)

        member_var = tk.StringVar()
        display_to_id: Dict[str, int] = {}

        def update_member_list(*args):
            nonlocal display_to_id
            for w in dynamic_frame.winfo_children():
                w.destroy()

            member_type = type_var.get()
            display_to_id.clear()

            if member_type == "Student":
                members = self.students or []
                id_key = "student_id"
                label_text = "Student:"
            else:
                members = self.teachers or []
                id_key = "teacher_id"
                label_text = "Teacher:"

            if not members:
                tk.Label(
                    dynamic_frame,
                    text=f"No {member_type.lower()}s available.",
                    font=("Segoe UI", 10),
                    bg=COLORS["bg_main"],
                    fg=COLORS["text_main"],
                ).pack()
                return

            for m in members:
                mid = m.get(id_key)
                name = m.get("full_name", f"{member_type} {mid}")
                if mid is None:
                    continue
                label = f"{mid} - {name}"
                display_to_id[label] = mid

            tk.Label(
                dynamic_frame,
                text=label_text,
                font=("Segoe UI", 10),
                bg=COLORS["bg_main"],
                fg=COLORS["text_main"],
            ).grid(row=0, column=0, sticky=tk.W, pady=(0, 10))

            combo = ttk.Combobox(
                dynamic_frame,
                textvariable=member_var,
                values=list(display_to_id.keys()),
                state="readonly",
                width=35,
            )
            combo.grid(row=0, column=1, sticky=tk.W, pady=(0, 10))
            if display_to_id:
                combo.current(0)

        type_var.trace("w", update_member_list)
        update_member_list()

        tk.Label(
            dialog,
            text="Group *:",
            font=("Segoe UI", 10),
            bg=COLORS["bg_main"],
            fg=COLORS["text_main"],
        ).grid(row=2, column=0, sticky=tk.W, padx=20, pady=10)

        group_entry = tk.Entry(dialog, font=("Segoe UI", 10), width=15)
        group_entry.grid(row=2, column=1, padx=20, pady=10, sticky=tk.W)

        def delete():
            try:
                member_type = type_var.get()
                selected_label = member_var.get()

                if not selected_label or selected_label not in display_to_id:
                    messagebox.showerror("Error", f"Please select a {member_type.lower()}")
                    return

                member_id = display_to_id[selected_label]
                raw_group = group_entry.get().strip()
                if raw_group == "":
                    messagebox.showerror("Error", "Please enter a group number")
                    return

                group_val = int(raw_group)
                group_display = str(group_val)

                if member_type == "Student":
                    ok = self.controller.get_member_controller().update_student_group(member_id, None)
                    if not ok:
                        messagebox.showerror("Error", "Student not found")
                        return
                    dialog.destroy()
                    messagebox.showinfo("Success", f"Student removed from group {group_display} successfully!")
                else:
                    # Teacher : supprimer l'event technique
                    teacher_name = selected_label.split(" - ", 1)[1] if " - " in selected_label else "Teacher"
                    target_name = f"[GROUP_LINK] {teacher_name} -> Group {group_val}"

                    # Vérifier que l'event existe
                    events = self.controller.get_event_controller().get_all_events()
                    found = any(ev.get("event_name") == target_name for ev in events)
                    if not found:
                        messagebox.showwarning(
                            "Warning",
                            f"No link found for this teacher in group {group_display}",
                        )
                        return

                    # On supprime directement sans autre confirmation
                    self.controller.get_event_controller().delete_event(target_name)

                    dialog.destroy()
                    messagebox.showinfo("Success", f"Teacher removed from group {group_display} successfully!")

            except ValueError:
                messagebox.showerror("Error", "Group must be a number")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to remove: {str(e)}")

        btn_frame = tk.Frame(dialog, bg=COLORS["bg_main"])
        btn_frame.grid(row=3, column=0, columnspan=2, pady=20)

        tk.Button(
            btn_frame,
            text="Delete",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["danger"],
            fg=COLORS["text_main"],
            padx=30,
            pady=8,
            command=delete,
        ).pack(side=tk.LEFT, padx=10)

        tk.Button(
            btn_frame,
            text="Cancel",
            font=("Segoe UI", 10),
            bg=COLORS["bg_panel"],
            fg=COLORS["text_main"],
            padx=30,
            pady=8,
            command=dialog.destroy,
        ).pack(side=tk.LEFT, padx=10)

    def _delete_event_dialog(self) -> None:
        event_name = simpledialog.askstring("Delete Event", "Enter Event Name:")
        if event_name:
            if self.controller.get_event_controller().delete_event(event_name):
                messagebox.showinfo("Success", "Event deleted successfully!")
            else:
                messagebox.showerror("Error", "Event not found!")

    def _delete_subscription_dialog(self) -> None:
        dialog = tk.Toplevel(self.root)
        dialog.title("Delete Subscription")
        dialog.configure(bg=COLORS["bg_main"])
        dialog.geometry("400x150")
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(
            dialog,
            text="Student ID:",
            font=("Segoe UI", 10),
            bg=COLORS["bg_main"],
            fg=COLORS["text_main"],
        ).grid(row=0, column=0, padx=20, pady=10)

        student_id_entry = tk.Entry(dialog, font=("Segoe UI", 10), width=20)
        student_id_entry.grid(row=0, column=1, padx=20, pady=10)

        tk.Label(
            dialog,
            text="Date (YYYY-MM-DD):",
            font=("Segoe UI", 10),
            bg=COLORS["bg_main"],
            fg=COLORS["text_main"],
        ).grid(row=1, column=0, padx=20, pady=10)

        date_entry = tk.Entry(dialog, font=("Segoe UI", 10), width=20)
        date_entry.grid(row=1, column=1, padx=20, pady=10)

        def delete():
            try:
                sid = int(student_id_entry.get())
                date = date_entry.get()
                if self.controller.get_finance_controller().delete_subscription(sid, date):
                    dialog.destroy()
                    messagebox.showinfo("Success", "Subscription deleted successfully!")
                else:
                    messagebox.showerror("Error", "Subscription not found!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete: {str(e)}")

        btn_frame = tk.Frame(dialog, bg=COLORS["bg_main"])
        btn_frame.grid(row=2, column=0, columnspan=2, pady=20)

        tk.Button(
            btn_frame,
            text="Delete",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["danger"],
            fg=COLORS["text_main"],
            padx=30,
            pady=8,
            command=delete,
        ).pack(side=tk.LEFT, padx=10)

        tk.Button(
            btn_frame,
            text="Cancel",
            font=("Segoe UI", 10),
            bg=COLORS["bg_panel"],
            fg=COLORS["text_main"],
            padx=30,
            pady=8,
            command=dialog.destroy,
        ).pack(side=tk.LEFT, padx=10)

    def _delete_donation_dialog(self) -> None:
        dialog = tk.Toplevel(self.root)
        dialog.title("Delete Donation")
        dialog.configure(bg=COLORS["bg_main"])
        dialog.geometry("400x200")
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(
            dialog,
            text="Donor Name:",
            font=("Segoe UI", 10),
            bg=COLORS["bg_main"],
            fg=COLORS["text_main"],
        ).grid(row=0, column=0, padx=20, pady=10)

        donor_entry = tk.Entry(dialog, font=("Segoe UI", 10), width=20)
        donor_entry.grid(row=0, column=1, padx=20, pady=10)

        tk.Label(
            dialog,
            text="Date (YYYY-MM-DD):",
            font=("Segoe UI", 10),
            bg=COLORS["bg_main"],
            fg=COLORS["text_main"],
        ).grid(row=1, column=0, padx=20, pady=10)

        date_entry = tk.Entry(dialog, font=("Segoe UI", 10), width=20)
        date_entry.grid(row=1, column=1, padx=20, pady=10)

        tk.Label(
            dialog,
            text="Amount:",
            font=("Segoe UI", 10),
            bg=COLORS["bg_main"],
            fg=COLORS["text_main"],
        ).grid(row=2, column=0, padx=20, pady=10)

        amount_entry = tk.Entry(dialog, font=("Segoe UI", 10), width=20)
        amount_entry.grid(row=2, column=1, padx=20, pady=10)

        def delete():
            try:
                donor = donor_entry.get()
                date = date_entry.get()
                amount = float(amount_entry.get())
                if self.controller.get_finance_controller().delete_donation(donor, date, amount):
                    dialog.destroy()
                    messagebox.showinfo("Success", "Donation deleted successfully!")
                else:
                    messagebox.showerror("Error", "Donation not found!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete: {str(e)}")

        btn_frame = tk.Frame(dialog, bg=COLORS["bg_main"])
        btn_frame.grid(row=3, column=0, columnspan=2, pady=20)

        tk.Button(
            btn_frame,
            text="Delete",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["danger"],
            fg=COLORS["text_main"],
            padx=30,
            pady=8,
            command=delete,
        ).pack(side=tk.LEFT, padx=10)

        tk.Button(
            btn_frame,
            text="Cancel",
            font=("Segoe UI", 10),
            bg=COLORS["bg_panel"],
            fg=COLORS["text_main"],
            padx=30,
            pady=8,
            command=dialog.destroy,
        ).pack(side=tk.LEFT, padx=10)

    # ------------------------------------------------------------------ Affichage principal

    def show_dashboard(self, project: Dict[str, Any]) -> None:
        members = project.get("members", [])
        events_raw = project.get("events", [])
        subs = project.get("subscriptions", [])
        donations = project.get("donations", [])

        self.students, self.teachers = _split_members(members)
        s_map, t_map = _build_member_maps(self.students, self.teachers)
        self.events = _parse_events(events_raw, s_map, t_map)
        self.subs = subs
        self.donations = donations

        self._populate_students_tab()
        self._populate_teachers_tab()
        self._populate_groups_tab()
        self._populate_events_tab()
        self._populate_subscriptions_tab()
        self._populate_donations_tab()

        self._switch_tab("students")
        self.root.mainloop()
