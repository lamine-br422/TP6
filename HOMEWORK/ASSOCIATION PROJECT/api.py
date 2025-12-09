"""
API FastAPI pour la gestion de l'association Madrassa
Cette API expose les opérations de gestion via des endpoints REST
"""
from __future__ import annotations
from pathlib import Path
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Query

from storage.json_storage import JSONStorage
from facades.association_facade import AssociationFacade
from interfaces.storage_interface import StorageInterface

# Initialisation de FastAPI
app = FastAPI(
    title="Madrassa Association Management API",
    description="API REST pour la gestion de l'association Madrassa",
    version="1.0.0"
)

# Initialisation du storage et de la Facade (pattern Facade)
base_dir = Path(__file__).parent
data_dir = base_dir / "data"
storage: StorageInterface = JSONStorage(data_dir)
facade = AssociationFacade(storage)


@app.get("/")
async def root():
    """Endpoint racine - retourne des informations sur l'API"""
    return {
        "message": "Bienvenue sur l'API de gestion de l'association Madrassa",
        "version": "1.0.0",
        "endpoints": {
            "dashboard": "/dashboard",
            "members": "/members",
            "students": "/members/students",
            "teachers": "/members/teachers",
            "events": "/events",
            "subscriptions": "/subscriptions",
            "donations": "/donations",
            "docs": "/docs"
        }
    }


@app.get("/dashboard")
async def get_dashboard() -> Dict[str, Any]:
    """Récupère toutes les données pour le tableau de bord"""
    return facade.get_dashboard_data()


@app.get("/statistics")
async def get_statistics() -> Dict[str, Any]:
    """Récupère les statistiques globales de l'association (utilise la Facade)"""
    return facade.get_statistics()


# ==================== ENDPOINTS POUR LES MEMBRES ====================

@app.get("/members")
async def get_all_members(
    sort_by: Optional[str] = Query(None, description="Critère de tri: name, date, group, status"),
    reverse: bool = Query(False, description="Trier en ordre décroissant")
) -> List[Dict[str, Any]]:
    """
    Récupère tous les membres (étudiants et professeurs).
    Utilise le pattern Strategy pour le tri.
    """
    return facade.get_all_members(sort_by, reverse)


@app.get("/members/students")
async def get_students(
    sort_by: Optional[str] = Query(None, description="Critère de tri: name, date, group, status"),
    reverse: bool = Query(False, description="Trier en ordre décroissant")
) -> List[Dict[str, Any]]:
    """
    Récupère uniquement les étudiants.
    Utilise le pattern Strategy pour le tri.
    """
    return facade.get_students(sort_by, reverse)


@app.get("/members/teachers")
async def get_teachers() -> List[Dict[str, Any]]:
    """Récupère uniquement les professeurs"""
    return facade.get_teachers()


@app.get("/members/student/{student_id}")
async def get_student_by_id(student_id: int) -> Dict[str, Any]:
    """Récupère un étudiant par son ID"""
    student = facade.get_member_by_id(student_id, "student")
    if student is None:
        raise HTTPException(status_code=404, detail=f"Étudiant avec ID {student_id} non trouvé")
    return student


@app.get("/members/teacher/{teacher_id}")
async def get_teacher_by_id(teacher_id: int) -> Dict[str, Any]:
    """Récupère un professeur par son ID"""
    teacher = facade.get_member_by_id(teacher_id, "teacher")
    if teacher is None:
        raise HTTPException(status_code=404, detail=f"Professeur avec ID {teacher_id} non trouvé")
    return teacher


# ==================== ENDPOINTS POUR LES ÉVÉNEMENTS ====================

@app.get("/events")
async def get_all_events() -> List[Dict[str, Any]]:
    """Récupère tous les événements"""
    return facade.get_all_events()


@app.get("/events/{event_name}")
async def get_event_by_name(event_name: str) -> Dict[str, Any]:
    """Récupère un événement par son nom"""
    event = facade.get_event_by_name(event_name)
    if event is None:
        raise HTTPException(status_code=404, detail=f"Événement '{event_name}' non trouvé")
    return event


@app.get("/events/date/{date}")
async def get_events_by_date(date: str) -> List[Dict[str, Any]]:
    """Récupère les événements pour une date donnée (format: YYYY-MM-DD)"""
    events = facade.get_events_by_date(date)
    return events


# ==================== ENDPOINTS POUR LES FINANCES ====================

@app.get("/subscriptions")
async def get_all_subscriptions() -> List[Dict[str, Any]]:
    """Récupère tous les abonnements"""
    return facade.get_all_subscriptions()


@app.get("/subscriptions/student/{student_id}")
async def get_subscriptions_by_student(student_id: int) -> List[Dict[str, Any]]:
    """Récupère les abonnements d'un étudiant spécifique"""
    subscriptions = facade.get_subscriptions_by_student(student_id)
    return subscriptions


@app.get("/subscriptions/status/{status}")
async def get_subscriptions_by_status(status: str) -> List[Dict[str, Any]]:
    """Récupère les abonnements par statut (paid, unpaid, pending)"""
    subscriptions = facade.get_subscriptions_by_status(status)
    return subscriptions


@app.get("/subscriptions/total")
async def get_total_subscriptions(status: Optional[str] = Query(None, description="Filtrer par statut: paid, unpaid, pending")) -> Dict[str, float]:
    """Calcule le total des abonnements, optionnellement filtré par statut"""
    try:
        total = facade.calculate_total_subscriptions(status)
        return {
            "total": total,
            "status": status if status else "all"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du calcul: {str(e)}")


@app.get("/donations")
async def get_all_donations() -> List[Dict[str, Any]]:
    """Récupère tous les dons"""
    return facade.get_all_donations()


@app.get("/donations/total")
async def get_total_donations() -> Dict[str, float]:
    """Calcule le total des dons"""
    total = facade.calculate_total_donations()
    return {"total": total}

