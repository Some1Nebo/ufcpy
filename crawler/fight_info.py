class FightInfo:
    def __init__(self, fighter1_ref, fighter2_ref, event_ref, outcome, method, round, time):
        self.fighter1_ref = fighter1_ref
        self.fighter2_ref = fighter2_ref
        self.event_ref = event_ref
        self.outcome = outcome
        self.method = method
        self.round = round
        self.time = time

    def __repr__(self):
        return "FightInfo({},{},{},{},{},{},{})".format(
            self.fighter1_ref,
            self.fighter2_ref,
            self.event_ref,
            self.outcome,
            self.method,
            self.round,
            self.time
        )