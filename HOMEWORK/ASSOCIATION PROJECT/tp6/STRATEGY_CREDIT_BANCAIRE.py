from abc import ABC, abstractmethod
import math

# ===============================
#       Strategy (interface)
# ===============================

class CreditStrategy(ABC):
    @abstractmethod
    def calculer_mensualite(self, capital, duree_mois, **kwargs):
        pass


# ===============================
#   Stratégies concrètes
# ===============================

class CreditSansInteret(CreditStrategy):
    def calculer_mensualite(self, capital, duree_mois, **kwargs):
        return capital / duree_mois


class CreditAvecInteret(CreditStrategy):
    def calculer_mensualite(self, capital, duree_mois, annual_rate=5, **kwargs):
        r = (annual_rate / 100) / 12  # taux mensuel
        if r == 0:
            return capital / duree_mois
        return capital * r / (1 - (1 + r) ** (-duree_mois))


# ===============================
#          Contexte
# ===============================

class PretBancaire:
    def __init__(self, strategy: CreditStrategy):
        self.strategy = strategy

    def set_strategy(self, nouvelle):
        self.strategy = nouvelle

    def mensualite(self, capital, duree_mois, **kwargs):
        return self.strategy.calculer_mensualite(capital, duree_mois, **kwargs)


# ===============================
#            Test
# ===============================

def main():
    pret = PretBancaire(CreditSansInteret())
    print("Sans intérêt :", pret.mensualite(10000, 24))

    pret.set_strategy(CreditAvecInteret())
    print("Avec intérêt :", pret.mensualite(10000, 24, annual_rate=5))

main()
