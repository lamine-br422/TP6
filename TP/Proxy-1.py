class StadiumAccess:
    def enter(self):
        print("Accès autorisé au stade")


class CovidPassProxy:
    def __init__(self, stadium_access, has_pass):
        self._stadium_access = stadium_access
        self._has_pass = has_pass

    def enter(self):
        if self._check_pass():
            self._stadium_access.enter()
        else:
            print("Accès refusé : pass sanitaire invalide ou absent")

    def _check_pass(self):
        print("Vérification du pass sanitaire")
        return self._has_pass


def main():
    real_access = StadiumAccess()
    proxy_ok = CovidPassProxy(real_access, True)
    proxy_bad = CovidPassProxy(real_access, False)
    proxy_ok.enter()
    proxy_bad.enter()
    return 0


if __name__ == "__main__":
    main()
