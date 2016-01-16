

class FighterRecord:
    def __init__(self, w_ko, w_submission, w_decision, l_ko, l_submission, l_decision):
        self.wins_ko = w_ko
        self.wins_submission = w_submission
        self.wins_decision = w_decision
        self.losses_ko = l_ko
        self.losses_submission = l_submission
        self.losses_decision = l_decision

    def wins(self):
        return self.wins_ko + self.wins_submission + self.wins_decision

    def losses(self):
        return self.losses_ko + self.losses_submission + self.losses_decision