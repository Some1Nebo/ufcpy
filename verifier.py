from random import random

import numpy as np
from sklearn import linear_model, preprocessing

from storage.models.fighter import Fighter
from storage import init_db
from storage.models.fight import Fight


class SVMPredictor:
    def __init__(self, featurize):
        # self.clf = svm.SVC(kernel='poly', degree=2, coef0=1)
        # self.clf = BernoulliNB()
        # self.clf = tree.DecisionTreeClassifier()

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
        print(data)

        # from sklearn.externals.six import StringIO
        # with open("iris.dot", 'w') as f:
        #    f = tree.export_graphviz(self.clf, out_file=f)

    def predict(self, fight):
        featurized = np.array([self.featurize(fight)])
        if self.scaler:
            featurized = self.scaler.transform(featurized)
            # print(featurized)
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

    return [
               age,
               fighter.height,
               fighter.reach,
               # win_ratio_feature,
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


class RandomPredictor:
    def learn(self, learning_set):
        pass

    def predict(self, fight):
        if random() < 0.5:
            return -1

        return 1


def reverse_fight(fight):
    return Fight(fighter1=fight.fighter2,
                 fighter2=fight.fighter1,
                 event=fight.event,
                 outcome=-fight.outcome)


def validate(predictor, validation_set):
    correct = 0
    predicted = 0

    for fight in validation_set:
        predicted_outcome = predictor.predict(fight)
        outcome = predicted_outcome
        # print(outcome)  # print to verify that it doesn't all predict -1 or 1

        if abs(outcome) > 0.15:
            outcome = -1 if outcome < 0 else 1
            predicted += 1
            if outcome == fight.outcome:
                correct += 1
                # print(fight.fighter1.ref, fight.fighter2.ref, outcome, predicted_outcome)

    return len(validation_set), correct, predicted, correct / float(predicted + 1e-10)


def cross_validate(predictor, fights):
    learning_ratio = 0.7
    n = len(fights)
    learning_size = int(n * learning_ratio)

    learning_set, validation_set = fights[:learning_size], fights[learning_size:]

    learning_set += map(reverse_fight, learning_set)
    predictor.learn(learning_set)

    reversed_validation_set = map(reverse_fight, validation_set)

    print(validate(predictor, validation_set))
    print(validate(predictor, reversed_validation_set))


if __name__ == "__main__":
    mysql_connection_string = "mysql+pymysql://{username}:{password}@{host}/{dbname}".format(
            username='tempuser',
            password='temppassword',
            host='localhost',
            dbname='ufcdb')

    memory_connection_string = 'sqlite:///:memory:'

    Session = init_db(mysql_connection_string, create=True)

    session = Session()

    fights = session.query(Fight).all()
    filtered_fights = [f for f in fights if f.fighter1.reach and f.fighter2.reach and f.event]

    # for f in filtered_fights:
        # print(featurize(f), f.fighter1.ref, f.fighter2.ref)

    #
    # fights_at_30 = filter(lambda f: "/events/UFC-Fight-Night-30-Machida-vs-Munoz-31371" in f.event.ref, fights)
    # lineker_fight = filter(lambda f: "Lineker" in f.fighter1.ref or "Lineker" in f.fighter2.ref, fights_at_30)[0]
    # print(lineker_fight.fighter1.ref)
    # print(featurize(lineker_fight))


    print("Total: {} fights".format(len(filtered_fights)))

    cross_validate(SVMPredictor(featurize), filtered_fights)
