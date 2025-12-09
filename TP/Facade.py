class DeptSite:
    def display(self):
        print("Affichage du site du département")

class ElearningInfo:
    def display(self):
        print("Affichage de la plateforme e-learning Info")

class UniversityElearning:
    def display(self):
        print("Affichage de la plateforme e-learning de l'université")

class FacebookPages:
    def display(self):
        print("Affichage des pages Facebook du département, faculté et université")

class StudentGroups:
    def display(self):
        print("Affichage des groupes étudiants")

class StudentResourcesFacade:
    def __init__(self):
        self.site = DeptSite()
        self.elearning_info = ElearningInfo()
        self.elearning_uni = UniversityElearning()
        self.facebook = FacebookPages()
        self.groups = StudentGroups()

    def show_all(self):
        self.site.display()
        self.elearning_info.display()
        self.elearning_uni.display()
        self.facebook.display()
        self.groups.display()

def main():
    facade = StudentResourcesFacade()
    facade.show_all()

if __name__ == "__main__":
    main()
