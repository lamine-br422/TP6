# ===============================
#   Sous-systèmes (ressources)
# ===============================

class DepartementSite:
    def afficher(self):
        print("Site du département : courses, annonces, contacts.")

class ELearningDept:
    def afficher(self):
        print("Plateforme e-learning du département : supports, TD, examens.")

class ELearningUniv:
    def afficher(self):
        print("Plateforme e-learning universitaire : MOOC et cours généraux.")

class FacebookPages:
    def afficher(self):
        print("Pages Facebook (Département, Faculté, Université) : annonces rapides.")

class StudentGroups:
    def afficher(self):
        print("Groupes étudiants : entraide, fichiers, organisation.")


# ===============================
#        Façade
# ===============================

class InfoFacade:
    def __init__(self):
        self.site = DepartementSite()
        self.elearn_dept = ELearningDept()
        self.elearn_univ = ELearningUniv()
        self.facebook = FacebookPages()
        self.groups = StudentGroups()

    def tout_afficher(self):
        print("\n=== Toutes les sources d'information ===")
        self.site.afficher()
        self.elearn_dept.afficher()
        self.elearn_univ.afficher()
        self.facebook.afficher()
        self.groups.afficher()

    def afficher_essentiel(self):
        print("\n=== Sources essentielles ===")
        self.site.afficher()
        self.elearn_dept.afficher()

    def afficher_reseaux(self):
        print("\n=== Réseaux sociaux ===")
        self.facebook.afficher()
        self.groups.afficher()


# ===============================
#          Test
# ===============================

def main():
    facade = InfoFacade()
    facade.tout_afficher()
    facade.afficher_essentiel()
    facade.afficher_reseaux()

main()
