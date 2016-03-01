from random import shuffle, random
from storage import init_db
from storage.models.fight import Fight
from storage.models.fighter import Fighter
from numpy import array, ndarray, asmatrix, transpose
from sklearn import svm


class SVMPredictor:
    def __init__(self, featurize):
        self.clf = svm.SVC(gamma=0.001, C=100.)
        self.featurize = featurize

    def learn(self, learning_set):
        raw_target = [float(f.outcome) for f in learning_set]
        target = array(raw_target)

        raw_data = [self.featurize(f) for f in learning_set]
        data = array(raw_data)

        self.clf.fit(data, target)

    def predict(self, fight):
        featurized = array([self.featurize(fight)])
        return self.clf.predict(featurized)[0]


def featurize(fight):
    return featurize_fighter(fight.fighter1, fight.event) + featurize_fighter(fight.fighter2, fight.event)


def featurize_fighter(fighter, event):
    previous_fights = [f for f in fighter.fights if f.event.date < event.date]
    wins = len([f for f in previous_fights if fighter_win(fighter, f)])
    losses = len(previous_fights) - wins
    win_ratio_feature = 0.5

    if len(previous_fights) != 0:
        win_ratio_feature = float(wins)/len(previous_fights)

    return [fighter.height, fighter.reach, win_ratio_feature]


def fighter_win(fighter, f):
    return f.fighter1.ref == fighter.ref and f.outcome == 1 or f.fighter2.ref == fighter.ref and f.outcome == -1


class RandomPredictor:
    def learn(self, learning_set):
        pass

    def predict(self, fight):
        if random() < 0.5:
            return -1

        return 1


def cross_validate(predictor, fights):
    shuffle(fights)
    learning_ratio = 0.8
    n = len(fights)
    learning_size = int(n * learning_ratio)
    learning_set, validation_set = fights[:learning_size], fights[learning_size:]

    predictor.learn(learning_set)

    correct = 0
    validation_size = len(validation_set)
    for fight in validation_set:
        outcome = predictor.predict(fight)

        if outcome == fight.outcome:
            correct += 1

    return correct / float(validation_size)


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
