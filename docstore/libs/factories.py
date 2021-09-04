from random import randint

from faker import Faker


fake = Faker()

def ListFactory(factory, **params):
    return [factory(**params) for n in range(randint(1, 5))]
