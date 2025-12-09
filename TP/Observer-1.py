class Subject:
    def __init__(self):
        self._observers = set()
        self._message = None

    def attach(self, observer):
        self._observers.add(observer)

    def detach(self, observer):
        self._observers.discard(observer)

    def notify(self):
        for o in self._observers:
            o.update(self._message)

    def new_post(self, message):
        self._message = message
        self.notify()


class Observer:
    def update(self, message):
        pass


class StudentObserver(Observer):
    def __init__(self, name):
        self.name = name

    def update(self, message):
        print(f"{self.name} a reçu une notification : {message}")


def main():
    dept_site = Subject()

    ali = StudentObserver("Ali")
    salma = StudentObserver("Salma")

    dept_site.attach(ali)
    dept_site.attach(salma)

    dept_site.new_post("Nouvelle annonce sur le site du département")

    dept_site.detach(ali)

    dept_site.new_post("Publication d'un nouveau TP")

if __name__ == "__main__":
    main()
