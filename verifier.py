from random import shuffle, random
from storage import init_db
from storage.models.fight import Fight
from storage.models.fighter import Fighter
import numpy as np
from sklearn import svm, linear_model, preprocessing
from sklearn.naive_bayes import BernoulliNB
from sklearn import tree


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

        # self.scaler = preprocessing.StandardScaler().fit(data)
        self.scaler = preprocessing.Normalizer().fit(data)
        if self.scaler:
            data = self.scaler.transform(data)

        self.clf.fit(data, target)
        print(data)

        #from sklearn.externals.six import StringIO
        #with open("iris.dot", 'w') as f:
        #    f = tree.export_graphviz(self.clf, out_file=f)

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
        win_ratio_feature = float(wins)/len(previous_fights)

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
        'wrestler': 0,
        'bjj': 0,
        'striker': 0,
        'cardio': 0,
        'boxing': 0,
        'chin': 0
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
    check('striker', ['ko', 'power', 'strik', 'kick', 'knee', 'elbow'])
    check('cardio', ['cardio', 'condition', 'athlet'])
    check('boxing', ['hands', 'box', 'ko', 'punch'])
    check('chin', ['heart', 'chin', 'resilience'])

    return [v for k, v in sorted(result.items(), key=lambda (name, value): name)]

class RandomPredictor:
    def learn(self, learning_set):
        pass

    def predict(self, fight):
        if random() < 0.5:
            return -1

        return 1


def cross_validate(predictor, fights):
    learning_ratio = 0.8
    n = len(fights)
    learning_size = int(n * learning_ratio)

    learning_set, validation_set = fights[:learning_size], fights[learning_size:]

    predictor.learn(learning_set)

    correct = 0
    predicted = 0

    for fight in validation_set:
        outcome = predictor.predict(fight)
        # print(outcome)  # print to verify that it doesn't all predict -1 or 1

        if abs(outcome) > 0.2:
            outcome = -1 if outcome < 0 else 1
            predicted += 1
            if outcome == fight.outcome:
                correct += 1
                print(fight.fighter1.ref, fight.fighter2.ref, outcome)

    return len(validation_set), correct, predicted, correct / float(predicted+1e-10)


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
    print("Total: {} fights".format(len(filtered_fights)))

    print(cross_validate(SVMPredictor(featurize), filtered_fights))
