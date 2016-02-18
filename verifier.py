from random import shuffle, random
from storage import init_db
from storage.models.fight import Fight
from storage.models.fighter import Fighter
from numpy import array, ndarray, asmatrix
from sklearn import svm

class SVMPredictor:
    def __init__(self, featurize):
        self.clf = svm.SVC(gamma=0.001, C=100.)
        self.featurize = featurize

    def learn(self, learning_set):
        target = array([f.outcome for f in learning_set])
        data = asmatrix([self.featurize(f) for f in learning_set])
        self.clf.fit(data, target)

    def predict(self, fight):
        featurized = self.featurize(fight)
        return self.clf.predict(featurized)[0]


def featurize(fight):
    return array(featurize_fighter(fight.fighter1, fight.event) + featurize_fighter(fight.fighter2, fight.event))


def featurize_fighter(fighter, event):
    return [fighter.height, fighter.reach]


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
    learning_size = int(n*learning_ratio)
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

    print(cross_validate(SVMPredictor(featurize), fights))