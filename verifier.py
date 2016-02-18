from random import shuffle, random
from storage import init_db
from storage.models.fight import Fight
from storage.models.fighter import Fighter


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

    print(cross_validate(RandomPredictor(), fights))