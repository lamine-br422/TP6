# ui/cli_ui.py
from typing import List

class CLIUI:
    def show_results(self, event_details: str, transactions: List[dict], project: dict | None = None) -> None:
        print(event_details)
        print("Transactions:")
        for t in transactions:
            print(" -", t)
        if project:
            print("\\n[Résumé projet] "
                  f"{len(project.get('students', []))} étudiants, "
                  f"{len(project.get('teachers', []))} profs, "
                  f"{len(project.get('events', []))} évènements, "
                  f"{len(project.get('subscriptions', []))} abonnements.")
