from abc import ABC, abstractmethod


class GitHub(ABC):
    @classmethod
    @abstractmethod
    def construct_url(cls, where, query, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def auth(self):
        raise NotImplementedError
