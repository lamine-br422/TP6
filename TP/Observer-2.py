class CalendarSubject:
    def __init__(self):
        self._observers = set()
        self._reminder = None

    def attach(self, observer):
        self._observers.add(observer)

    def detach(self, observer):
        self._observers.discard(observer)

    def notify(self):
        for o in self._observers:
            o.update(self._reminder)

    def set_reminder(self, reminder):
        self._reminder = reminder
        self.notify()


class UserObserver:
    def __init__(self, username):
        self.username = username

    def update(self, reminder):
        print(f"{self.username} a reçu un rappel : {reminder}")


def main():
    calendar = CalendarSubject()

    user1 = UserObserver("Ahmed")
    user2 = UserObserver("Yasmina")

    calendar.attach(user1)
    calendar.attach(user2)

    calendar.set_reminder("Rendez-vous demain à 9h")

    calendar.detach(user1)

    calendar.set_reminder("Examen jeudi prochain")

if __name__ == "__main__":
    main()
