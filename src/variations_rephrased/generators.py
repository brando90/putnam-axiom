import random
import string
import math


class Generator:
    def sample(self, sampled_params=None):
        """
        Generate a sample from the distribution.
        :param sampled_params: A dictionary of parameters that have already been sampled
        :return: A sample from the distribution
        """
        raise NotImplementedError


class Literal(Generator):
    def __init__(self, value):
        self.value = value

    def sample(self, sampled_params=None):
        return self.value


class RandomInt(Generator):
    def __init__(self, min, max):
        self.min = min
        self.max = max

    def sample(self, sampled_params=None):
        return random.randint(self.min, self.max)


class RandomFloat(Generator):
    def __init__(self, min, max):
        self.min = min
        self.max = max

    def sample(self, sampled_params=None):
        return random.uniform(self.min, self.max)


class RandomPrime(Generator):
    def __init__(self, min, max, n=1):
        self.min = min
        self.max = max
        self.n = n

    @staticmethod
    def is_prime(n):
        if n <= 1 or (n % 2 == 0 and n > 2):
            return False
        return all(n % i for i in range(3, int(math.sqrt(n)) + 1, 2))

    def _sample(self, sampled_params=None):
        while True:
            num = random.randint(self.min, self.max)
            if self.is_prime(num):
                return num

    def sample(self, sampled_params=None):
        return [self._sample(sampled_params) for _ in range(self.n)]


class RandomVariable(Generator):
    def __init__(self, available_values='both'):
        if available_values == 'lower':
            characters = string.ascii_lowercase
        elif available_values == 'upper':
            characters = string.ascii_uppercase
        else:
            characters = string.ascii_letters
        self.characters = characters

    def sample(self, sampled_params=None):
        # assumes that all characters in sampled_params that are found in self.characters are other sampled variables
        remaining_characters = set(self.characters)
        for v in sampled_params.values():
            if v in remaining_characters:
                remaining_characters.remove(v)

        return random.choice(list(remaining_characters))
