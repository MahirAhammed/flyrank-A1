from abc import ABC, abstractmethod

class Database(ABC):

    @abstractmethod
    def get_placeholder(self) -> str:
        """SQL parameter placeholder used for queries."""
        raise NotImplementedError

    @abstractmethod
    def get_connection(self):
        raise NotImplementedError

    @abstractmethod
    def init_db(self):
        raise NotImplementedError

    def ping(self):
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.fetchone()
        conn.commit()
        conn.close()