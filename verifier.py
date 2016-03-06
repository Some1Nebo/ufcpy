from datetime import datetime

import numpy as np
from sklearn import linear_model, preprocessing

from storage import init_db
from storage.models.fight import Fight
from storage.models.fighter import Fighter

cutoff_date = datetime(year=1970, month=1, day=1).date()


class MLPredictor:
    def __init__(self, featurize):
        self.clf = linear_model.LassoCV()

        self.featurize = featurize
        self.scaler = None

    def learn(self, learning_set):
        raw_target = [f.outcome for f in learning_set]
        target = np.array(raw_target)

        raw_data = [self.featurize(f) for f in learning_set]
        data = np.array(raw_data)

        self.scaler = preprocessing.StandardScaler().fit(data)
        # self.scaler = preprocessing.Normalizer().fit(data)

        if self.scaler:
            data = self.scaler.transform(data)

        self.clf.fit(data, target)

    def predict(self, fight):
        featurized = np.array([self.featurize(fight)])
        if self.scaler:
            featurized = self.scaler.transform(featurized)
        return self.clf.predict(featurized)[0]


def featurize(fight):
    return featurize_fighter(fight.fighter1, fight.event) + featurize_fighter(fight.fighter2, fight.event)


def featurize_fighter(fighter, event):
    previous_fights = [f for f in fighter.fights if f.event.date < event.date]
    previous_fights.sort(key=lambda f: f.event.date)
    wins = len([f for f in previous_fights if fighter_win(fighter, f)])
    losses = len(previous_fights) - wins
    win_ratio_feature = 0.5

    if len(previous_fights) != 0:
        win_ratio_feature = float(wins) / len(previous_fights)

    age = (event.date - fighter.birthday).days / 365.0

    return [age,
            fighter.height,
            fighter.reach,
            wins,
            losses,
            win_ratio_feature,
            winning_streak(fighter, previous_fights)
            ] + specialization_vector(fighter)


def winning_streak(figher, previous_fights):
    streak = 0

    for f in reversed(previous_fights):
        if fighter_win(figher, f):
            streak += 1
        else:
            break

    return streak


def fighter_win(fighter, f):
    return f.fighter1.ref == fighter.ref and f.outcome == 1 or f.fighter2.ref == fighter.ref and f.outcome == -1


def specialization_vector(fighter):
    result = {
        'bjj': 0,
        'boxing': 0,
        'cardio': 0,
        'chin': 0,
        'striker': 0,
        'wrestler': 0
    }

    spec = fighter.specialization or ''
    spec = spec.lower()

    def check(category, words):
        for w in words:
            if w in spec:
                result[category] = 1
                break

    check('wrestler', ['wrestl', 'takedown', 'slam', 'throw'])
    check('bjj', ['bjj', 'jiu', 'jits', 'grappl', 'ground', 'submission'])
    check('striker', ['ko ', 'power', 'strik', 'kick', 'knee', 'elbow', 'muay', 'thai'])
    check('cardio', ['cardio', 'condition', 'athlet'])
    check('boxing', ['hands', 'box', 'ko ', 'punch'])
    check('chin', ['heart', 'chin', 'resilience'])

    return [v for k, v in sorted(result.items(), key=lambda (name, value): name)]


class EventProxy:
    def __init__(self, date):
        self.date = date


class FightProxy:
    def __init__(self, fighter1, fighter2, event):
        self.fighter1 = fighter1
        self.fighter2 = fighter2
        self.event = event

    @staticmethod
    def reversed(fight):
        result = FightProxy(fight.fighter2, fight.fighter1, fight.event)
        result.outcome = -fight.outcome
        return result


def cross_validate(predictor, fights):
    learning_set, validation_set = split(fights, 0.7)
    learning_set += map(FightProxy.reversed, learning_set)
    predictor.learn(learning_set)

    correct = 0
    predicted = 0

    for fight in validation_set:
        outcome = predictor.predict(fight)

        if abs(outcome) > 0.2:
            predicted_outcome = -1 if outcome < 0 else 1
            predicted += 1
            if predicted_outcome == fight.outcome:
                correct += 1

            print(fight.fighter1.ref, fight.fighter2.ref, fight.outcome, outcome)
            print(featurize(fight))

    return len(validation_set), correct, predicted, correct / float(predicted + 1e-10)


def split(collection, ratio):
    mid = int(len(collection) * ratio)
    return collection[:mid], collection[mid:]


def validate_fight(f):
    return (f.fighter1.reach and
            f.fighter2.reach and
            f.event and
            f.fighter1.birthday > cutoff_date and
            f.fighter2.birthday > cutoff_date)


def find_fighter(fighters, name):
    first_name, last_name = name.lower().split()
    return filter(lambda f: first_name in f.ref.lower() and last_name in f.ref.lower(), fighters)[0]


def predict_event(predictor, fights, fighters):
    event_date_str = raw_input("Enter event date (DD/MM/YYYY): ")
    event_date = datetime.strptime(event_date_str, "%d/%m/%Y").date()
    print(event_date)

    predictor.learn(fights)

    while True:
        name1 = raw_input("Enter fighter 1 name: ")
        fighter1 = find_fighter(fighters, name1)
        print(fighter1.ref)

        name2 = raw_input("Enter fighter 2 name: ")
        fighter2 = find_fighter(fighters, name2)
        print(fighter2.ref)

        fight = FightProxy(fighter1, fighter2, EventProxy(event_date))
        print(featurize(fight))

        print(predictor.predict(fight))


if __name__ == "__main__":
    mysql_connection_string = "mysql+pymysql://{username}:{password}@{host}/{dbname}".format(
            username='tempuser',
            password='temppassword',
            host='localhost',
            dbname='ufcdb')

    memory_connection_string = 'sqlite:///:memory:'

    Session = init_db(mysql_connection_string, create=True)

    session = Session()

    all_fights = session.query(Fight).all()
    fights = filter(validate_fight, all_fights)
    fighters = session.query(Fighter).all()

    predictor = MLPredictor(featurize)

    # print(cross_validate(predictor, fights))

    predict_event(predictor, fights, fighters)
