import copy
from cached_property import cached_property
from mgba_gamedata.memory import Endian, ParentAdapter


class Type(object):
    _memory = ParentAdapter()
    _parent = None

    def __init__(self, address=0, segment=None):
        self._address = address
        self._segment = segment

    @cached_property
    def address(self):
        if self._parent is None:
            return self._address
        return self._parent.address + self._address

    def _reparent(self, parent):
        self._parent = parent


class List(Type):
    def __init__(self, element_template, element_count, address=0, segment=None):
        super(List, self).__init__(address, segment)
        self._size = element_template._size * element_count
        self._list = []
        for i in xrange(element_count):
            element = copy.copy(element_template)
            element._address += i * element._size
            element._reparent(self)
            self._list.append(element)

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

    def _reparent(self, parent):
        super(List, self)._reparent(parent)
        for element in self._list:
            element._reparent(self)


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
                    offset = value._address + value._size
                    if offset > max_offset:
                        max_offset = offset
            if '_size' not in attrs:
                attrs['_size'] = max_offset

        attrs['_children'] = children
        return super(StructType, cls).__new__(cls, name, bases, attrs)


class Struct(Type):
    __metaclass__ = StructType

    def __init__(self, fields={}, address=0, segment=None):
        super(Struct, self).__init__(address, segment)

        for name, field in fields.iteritems():
            self._children.append(name)
            setattr(self, name, field)

        for child in self._children:
            getattr(self, child)._reparent(self)

    def _reparent(self, parent):
        super(Struct, self)._reparent(parent)
        for child in self._children:
            getattr(self, child)._reparent(self)


class Value(Type):
    def __init__(self, width, address=0, segment=None, endian=Endian.LITTLE, signed=False):
        super(Value, self).__init__(address, segment)

        self._width = width
        self._size = width
        self._endian = endian
        self._signed = signed

    def __get__(self, ob, cls=None):
        base = ob.address
        rawmem = ob._memory[base + self._address:base + self._address + self._width]
        value = 0
        if self._endian == Endian.LITTLE:
            i = 0
            for b in rawmem:
                value |= b << (i * 8)
                i += 1
        else:
            for b in rawmem:
                value <<= 8
                value |= b
        if self._signed:
            m = 0x80 << (8 * (self._width - 1))
            if value >= m:
                value = ~((m << 1) - value - 1)
        return value

    def __set__(self, ob, value):
        base = ob.address
        if self._endian == Endian.LITTLE:
            i = 0
            for i in xrange(self._width):
                ob._memory[base + self._address + i] = value & 0xFF
                value >>= 8
                i += 1
        else:
            i = 0
            for i in xrange(self._width):
                ob._memory[base + self._address + self._width - i - 1] = value & 0xFF
                value >>= 8
                i += 1


class Character(Value):
    def __init__(self, address=0, segment=None):
        super(Character, self).__init__(width=self._width, address=address, segment=segment)

    def __get__(self, ob, cls=None):
        c = super(Character, self).__get__(ob, cls)
        return self._mapping[c]


class String(List):
    def __init__(self, length, address=0, segment=None):
        super(String, self).__init__(self._characters(), length, address=address, segment=segment)

    def __str__(self):
        text = []
        for c in self:
            if hasattr(self, '_terminator') and c == self._terminator:
                break
            text.append(c)
        return ''.join(text)
