class Strategy:
    def verifier(self, moyenne, credits, unites_valides):
        pass


class StrategyMoyenne(Strategy):
    def verifier(self, moyenne, credits, unites_valides):
        return moyenne >= 10


class StrategyCredits(Strategy):
    def verifier(self, moyenne, credits, unites_valides):
        return credits >= 180


class StrategyMixte(Strategy):
    def verifier(self, moyenne, credits, unites_valides):
        return moyenne >= 10 and unites_valides


class EtudiantContext:
    def __init__(self, strategy):
        self.strategy = strategy

    def peut_passer(self, moyenne, credits, unites_valides):
        return self.strategy.verifier(moyenne, credits, unites_valides)


def main():
    moyenne = 12
    credits = 180
    unites_valides = True

    # Exemple : on utilise la stratégie mixte
    strategie = StrategyMixte()
    etudiant = EtudiantContext(strategie)

    resultat = etudiant.peut_passer(moyenne, credits, unites_valides)

    if resultat:
        print("Décision : Admis.")
    else:
        print("Décision : Ajourné.")


if __name__ == "__main__":
    main()
