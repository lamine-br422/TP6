from abc import ABC, abstractmethod

# ===============================
#         Strategy
# ===============================

class TransitionStrategy(ABC):
    @abstractmethod
    def check_transition(self, moyenne, credits):
        pass


# ===============================
#   Stratégies concrètes
# ===============================

class LicenceToMaster(TransitionStrategy):
    def check_transition(self, moyenne, credits):
        if moyenne >= 12 and credits >= 45:
            return "Admis en Master"
        return "Refusé (conditions non atteintes)"


class LicenceToLicence(TransitionStrategy):
    def check_transition(self, moyenne, credits):
        if moyenne >= 10 and credits >= 45:
            return "Passage vers l'année supérieure"
        return "Redoublement"


# ===============================
#           Contexte
# ===============================

class Etudiant:
    def __init__(self, strategy: TransitionStrategy):
        self.strategy = strategy

    def verifier_passage(self, moyenne, credits):
        return self.strategy.check_transition(moyenne, credits)

    def set_strategy(self, new_strategy):
        self.strategy = new_strategy


# ===============================
#             Test
# ===============================

def main():
    e = Etudiant(LicenceToMaster())
    print(e.verifier_passage(13, 48))

    e.set_strategy(LicenceToLicence())
    print(e.verifier_passage(9, 50))

main()
