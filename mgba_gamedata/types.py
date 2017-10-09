import copy
from mgba_gamedata.memory import Endian


class Type(object):
    _memory = None

    def __init__(self, address=0, segment=None):
        self.address = address
        self.segment = segment

    def instantiate(self, memory, address=0):
        self._memory = memory
        self.address += address


class List(Type):
    def __init__(self, element_template, element_count, address=0, segment=None):
        super(List, self).__init__(address, segment)
        self.size = element_template.size * element_count
        self._list = []
        for i in xrange(element_count):
            element = copy.copy(element_template)
            element.address += i * element.size
            self._list.append(element)

    def instantiate(self, memory, address=0):
        super(List, self).instantiate(memory, address)
        new_list = []
        for element in self._list:
            if isinstance(element, Value):
                return
            element = copy.copy(element)
            element.instantiate(memory, self.address)
            new_list.append(element)
        self._list = new_list

    def __len__(self):
        return len(self._list)

    def __getitem__(self, index):
        item = self._list[index]
        if isinstance(item, Value):
            return item.__get__(self, self.__class__)
        else:
            return item

    def __setitem__(self, index, value):
        self._list[index] = value


class StructType(type):
    def __new__(cls, name, bases, attrs):
        children = []
        for base in bases:
            if hasattr(base, '_children'):
                children.extend(base._children)
        if name != 'Struct':
            max_offset = 0
            for aname, value in attrs.iteritems():
                if isinstance(value, Type):
                    if not isinstance(value, Value):
                        children.append(aname)
                    offset = value.address + value.size
                    if offset > max_offset:
                        max_offset = offset
            if 'size' not in attrs:
                attrs['size'] = max_offset

        attrs['_children'] = children
        return super(StructType, cls).__new__(cls, name, bases, attrs)


class Struct(Type):
    __metaclass__ = StructType

    def __init__(self, fields={}, address=0, segment=None):
        super(Struct, self).__init__(address, segment)

        for name, field in fields.iteritems():
            self._children.append(name)
            setattr(self, name, field)

    def instantiate(self, memory, address=0):
        super(Struct, self).instantiate(memory, address)
        for child in self._children:
            c = getattr(self, child)
            c = copy.copy(c)
            c.instantiate(memory, self.address)
            setattr(self, child, c)


class Value(Type):
    def __init__(self, width, address=0, segment=None, endian=Endian.LITTLE, signed=False):
        super(Value, self).__init__(address, segment)

        self.width = width
        self.size = width
        self.endian = endian
        self.signed = signed

    def __get__(self, ob, cls=None):
        base = ob.address
        rawmem = ob._memory[base + self.address:base +self.address + self.width]
        value = 0
        if self.endian == Endian.LITTLE:
            i = 0
            for b in rawmem:
                value |= b << (i * 8)
                i += 1
        else:
            for b in rawmem:
                value <<= 8
                value |= b
        if self.signed:
            m = 0x80 << (8 * (self.width - 1))
            if value >= m:
                value = ~((m << 1) - value - 1)
        return b

    def __set__(self, ob, value):
        raise NotImplementedError


class Character(Value):
    def __init__(self, address=0, segment=None):
        super(Character, self).__init__(width=self.width, address=address, segment=segment)

    def __get__(self, ob, cls=None):
        c = super(Character, self).__get__(ob, cls)
        return self.mapping[c]


class String(List):
    def __init__(self, length, address=0, segment=None):
        super(String, self).__init__(self.characters(), length, address=address, segment=segment)

    def __str__(self):
        text = []
        for c in self:
            if hasattr(self, 'terminator') and c == self.terminator:
                break
            text.append(c)
        return ''.join(text)
