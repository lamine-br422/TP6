class DateMachine:
    def __init__(self, year, month, day):
        self.year = year
        self.month = month
        self.day = day


class DateUS:
    def __init__(self, date_machine):
        self.date = f"{date_machine.month:02d}/{date_machine.day:02d}/{date_machine.year}"


class DateEU:
    def __init__(self, date_machine):
        self.date = f"{date_machine.day:02d}/{date_machine.month:02d}/{date_machine.year}"


def main():
    d = DateMachine(2025, 12, 6)
    us = DateUS(d)
    eu = DateEU(d)
    print("MM/DD/YYYY :", us.date)
    print("DD/MM/YYYY :", eu.date)
    return 0


if __name__ == "__main__":
    main()
