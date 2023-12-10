from abc import ABC, abstractmethod
from typing import Set


class BaseCITest(ABC):

    @abstractmethod
    def __call__(self, x: int, y: int, cond_set: Set[int]):
        pass

