from __future__ import annotations
from pathlib import Path
from interfaces.storage_interface import StorageInterface
from interfaces.ui_interface import UIInterface
from storage.json_storage import JSONStorage
from views.web_view import WebUI
from facades.association_facade import AssociationFacade


def run_application(storage: StorageInterface, ui: UIInterface) -> None:
    # Utilisation du pattern Facade : interface simplifiée pour accéder aux services
    facade = AssociationFacade(storage)
    
    # La Facade récupère toutes les données nécessaires de manière simplifiée
    project = facade.get_dashboard_data()
    
    # La vue affiche les données
    ui.show_dashboard(project)


if __name__ == "__main__":
    base_dir = Path(__file__).parent
    data_dir = base_dir / "data"
    out_file = base_dir / "site" / "madrassa.html"

    storage: StorageInterface = JSONStorage(data_dir)
    ui: UIInterface = WebUI(out_file)

    run_application(storage, ui)
