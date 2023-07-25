from multiprocessing.managers import BaseManager


class TranspositionTable:
    def __init__(self, size=2_000_000):
        self.size = size
        self.table = {}
    def __getitem__(self, key):
        return self.table.get(key)

    def __setitem__(self, key, value):
        if len(self.table) >= self.size:
            self.table.clear()
            print('TT cleared')
        self.table[key] = value

    def clone(self,obj):
        self.table = obj.table.copy()
        self.size = obj.size
        return self

    def get(self, key):
        return self.table.get(key)
    
    def set(self, key, value):
        if len(self.table) >= self.size:
            self.table.clear()
            print('TT cleared')
        self.table[key] = value

#custom manager
class TTManager(BaseManager):
    pass