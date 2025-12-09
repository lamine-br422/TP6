# 📌 Homework — Design Patterns (Projet Madrassa)

Gestion d’Association (Madrassa)

Ce travail améliore l’architecture du projet en intégrant deux Design Patterns essentiels :  
un pattern Structural (**Facade**) et un pattern Behavioral (**Strategy**).  
L’objectif est de simplifier l’accès aux services internes, d’améliorer la lisibilité du code  
et de rendre le tri des membres flexible et extensible.

---

## 🎯 Objectifs du projet

- Ajouter des Design Patterns pour renforcer l’architecture
- Réduire le couplage entre les parties du système
- Centraliser l’accès aux contrôleurs via une **Facade**
- Rendre le tri dynamique grâce au **Strategy Pattern**
- Assurer un code plus propre, maintenable et extensible

---

## 🧱 Pattern Facade

- Fournit une **interface unique** pour accéder aux membres, événements et finances  
- Remplace les appels directs à plusieurs contrôleurs  
- Ajoute une méthode centralisée : `get_statistics()`  
- Simplifie fortement le code client

---

## 🧠 Pattern Strategy

- Permet de changer la stratégie de tri à l’exécution  
- 4 stratégies implémentées : **nom**, **date**, **groupe**, **statut**  
- Améliore la modularité et la réutilisation du code  
- Intégré dans `MemberController` et exposé via la Facade

---

## 📁 Fichiers ajoutés / modifiés

- `facades/association_facade.py` → nouvelle interface unifiée  
- `strategies/` → toutes les stratégies de tri  
- `member_controller.py` → support du tri dynamique  

---

## ✅ Résultat

Grâce aux patterns **Facade** et **Strategy**,  
le projet est désormais plus clair, mieux organisé, plus flexible  
et prêt pour de futures évolutions.  
