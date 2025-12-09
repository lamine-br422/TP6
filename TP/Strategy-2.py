class StrategyCredit:
    def calculer(self, montant):
        pass


class StrategySansInteret(StrategyCredit):
    def calculer(self, montant):
        return montant


class StrategyAvecInteret(StrategyCredit):
    def __init__(self, taux):
        self.taux = taux

    def calculer(self, montant):
        return montant * (1 + self.taux)


class CreditContext:
    def __init__(self, strategy):
        self.strategy = strategy

    def obtenir_total(self, montant):
        return self.strategy.calculer(montant)


def main():
    montant = 100000

    # Crédit avec intérêt (ex : 5%)
    strategie1 = StrategyAvecInteret(taux=0.05)
    contexte1 = CreditContext(strategie1)
    total1 = contexte1.obtenir_total(montant)
    print(f"Crédit avec intérêt : {total1} DA")

    # Crédit sans intérêt
    strategie2 = StrategySansInteret()
    contexte2 = CreditContext(strategie2)
    total2 = contexte2.obtenir_total(montant)
    print(f"Crédit sans intérêt : {total2} DA")


if __name__ == "__main__":
    main()
