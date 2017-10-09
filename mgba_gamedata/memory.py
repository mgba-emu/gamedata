class Endian:
    LITTLE = 'little'
    BIG = 'big'


class Adapter(object):
    def __getitem__(self, index):
        raise NotImplementedError

    def __setitem__(self, index, value):
        raise NotImplementedError
