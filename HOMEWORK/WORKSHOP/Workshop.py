class AccessService:
    def enter(self, person_name):
        raise NotImplementedError


class StadiumAccess(AccessService):
    def enter(self, person_name):
        print(person_name, "entre dans le stade")


class HealthPassProxy(AccessService):
    def __init__(self, real_service):
        self.real_service = real_service

    def enter(self, person_name, has_pass=False):
        if has_pass:
            print("Pass sanitaire valide pour", person_name)
            self.real_service.enter(person_name)
        else:
            print("Accès refusé pour", person_name, ": pass sanitaire invalide")


class ServiceVisa:
    def deposer_dossier(self, nom_demandeur, dossier):
        raise NotImplementedError


class ServiceAmbassade(ServiceVisa):
    def deposer_dossier(self, nom_demandeur, dossier):
        print("Ambassade: dossier de", nom_demandeur, "reçu :", dossier)


class ProxyAgenceVisa(ServiceVisa):
    def __init__(self, service_reel):
        self.service_reel = service_reel

    def deposer_dossier(self, nom_demandeur, dossier):
        print("Agence: vérification du dossier de", nom_demandeur)
        if dossier.get("frais_payes") and dossier.get("formulaire_complet"):
            print("Agence: dossier complet, envoi à l’ambassade")
            self.service_reel.deposer_dossier(nom_demandeur, dossier)
        else:
            print("Agence: dossier incomplet, refus d’envoi pour", nom_demandeur)


class Subject:
    def __init__(self):
        self._observers = set()

    def attach(self, observer):
        self._observers.add(observer)

    def detach(self, observer):
        self._observers.discard(observer)

    def notify(self, message):
        for observer in self._observers:
            observer.update(message)


class Observer:
    def update(self, message):
        raise NotImplementedError


class StudentObserver(Observer):
    def __init__(self, name):
        self.name = name
        self.last_message = None

    def update(self, message):
        self.last_message = message
        print("Étudiant", self.name, "a reçu la notification :", message)


class DepartmentSite(Subject):
    def publier_nouveau_post(self, titre):
        message = "Nouveau post sur le site du département : " + titre
        self.notify(message)


class Calendar(Subject):
    def ajouter_evenement(self, titre):
        message = "Rappel de calendrier : " + titre
        self.notify(message)


def demo_proxy():
    print("=== Proxy Q1: contrôle pass sanitaire stade ===")
    real_access = StadiumAccess()
    proxy_access = HealthPassProxy(real_access)
    proxy_access.enter("Ali", has_pass=True)
    proxy_access.enter("Sara", has_pass=False)

    print("\n=== Proxy Q2: dépôt de dossier de visa via agence ===")
    ambassade = ServiceAmbassade()
    agence = ProxyAgenceVisa(ambassade)
    dossier_complet = {"frais_payes": True, "formulaire_complet": True}
    dossier_incomplet = {"frais_payes": False, "formulaire_complet": True}
    agence.deposer_dossier("Youssef", dossier_complet)
    agence.deposer_dossier("Meriem", dossier_incomplet)


def demo_observer():
    print("\n=== Observer Q1: notifications site du département ===")
    site = DepartmentSite()
    etu1 = StudentObserver("Ahmed")
    etu2 = StudentObserver("Salima")
    site.attach(etu1)
    site.attach(etu2)
    site.publier_nouveau_post("Annonce examen RCB")

    print("\n=== Observer Q2: rappels de calendrier ===")
    calendrier = Calendar()
    user1 = StudentObserver("Karim")
    user2 = StudentObserver("Nadia")
    calendrier.attach(user1)
    calendrier.attach(user2)
    calendrier.ajouter_evenement("TP design patterns demain à 10h")


def main():
    demo_proxy()
    demo_observer()


if __name__ == "__main__":
    main()
