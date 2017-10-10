# -*- coding: utf-8 -*-
from mgba_gamedata.types import Struct, Value, List, Character, String, Endian
from mgba_gamedata.gb import GBGame


class Gen1CharacterE(Character):
    _width = 1

    _mapping = [
        # 0x0X
        u'�', u'�', u'�', u'�', u'�', u'�', u'�', u'�',
        u'�', u'�', u'�', u'�', u'�', u'�', u'�', u'�',

        # 0x1X
        u'�', u'�', u'�', u'�', u'�', u'�', u'�', u'�',
        u'�', u'�', u'�', u'�', u'�', u'�', u'�', u'�',

        # 0x2X
        u'�', u'�', u'�', u'�', u'�', u'�', u'�', u'�',
        u'�', u'�', u'�', u'�', u'�', u'�', u'�', u'�',

        # 0x3X
        u'�', u'�', u'�', u'�', u'�', u'�', u'�', u'�',
        u'�', u'�', u'�', u'�', u'�', u'�', u'�', u'�',

        # 0x4X
        u'�', u'�', u'�', u'�', u'�', u'�', u'�', u'�',
        u'�', u'�', u'�', u'�', u'�', u'�', u'�', u'�',

        # 0x5X
        u'\x00', u'�', u'�', u'�', u'�', u'�', u'�', u'�',
        u'�', u'�', u'�', u'�', u'�', u'�', u'�', u'�',

        # 0x6X
        u'�', u'�', u'�', u'�', u'�', u'�', u'�', u'�',
        u'�', u'�', u'�', u'�', u'�', u'�', u'�', u'�',

        # 0x7X
        u'�', u'�', u'�', u'�', u'�', u'�', u'�', u'�',
        u'�', u'�', u'�', u'�', u'�', u'�', u'�', u' ',

        # 0x8X
        u'A', u'B', u'C', u'D', u'E', u'F', u'G', u'H',
        u'I', u'J', u'K', u'L', u'M', u'N', u'O', u'P',

        # 0x9X
        u'Q', u'R', u'S', u'T', u'U', u'V', u'W', u'X',
        u'Y', u'Z', u'(', u')', u':', u';', u'[', u']',

        # 0xAX
        u'a', u'b', u'c', u'd', u'e', u'f', u'g', u'h',
        u'i', u'j', u'k', u'l', u'm', u'n', u'o', u'p',

        # 0xBX
        u'q', u'r', u's', u't', u'u', u'v', u'w', u'x',
        u'y', u'z', u'é', u'ʼd', u'ʼl', u'ʼs', u'ʼt', u'ʼv',

        # 0xCX
        u'�', u'�', u'�', u'�', u'�', u'�', u'�', u'�',
        u'�', u'�', u'�', u'�', u'�', u'�', u'�', u'�',

        # 0xDX
        u'�', u'�', u'�', u'�', u'�', u'�', u'�', u'�',
        u'�', u'�', u'�', u'�', u'�', u'�', u'�', u'�',

        # 0xEX
        u'\'', u'P\u200dk', u'M\u200dn', u'-', u'ʼr', u'ʼm', u'?', u'!',
        u'.', u'ァ', u'ゥ', u'ェ', u'▹', u'▸', u'▾', u'♂',

        # 0xFX
        u'$', u'×', u'.', u'/', u',', u'♀', u'0', u'1',
        u'2', u'3', u'4', u'5', u'6', u'7', u'8', u'9'
    ]


class Gen1StringE(String):
    _characters = Gen1CharacterE
    _terminator = u'\x00'


class BoxMon(Struct):
    species = Value(width=1, address=0)
    hp = Value(width=2, address=1, endian=Endian.BIG)
    level = Value(width=1, address=3)
    status = Value(width=1, address=4)
    type1 = Value(width=1, address=5)
    type2 = Value(width=1, address=6)
    catch_rate = Value(width=1, address=7)
    moves = List(Value(width=1), 4, address=8)
    ot_id = Value(width=2, address=12, endian=Endian.BIG)
    exp = Value(width=3, address=14, endian=Endian.BIG)
    hp_ev = Value(width=2, address=17, endian=Endian.BIG)
    attack_ev = Value(width=2, address=19, endian=Endian.BIG)
    defense_ev = Value(width=2, address=21, endian=Endian.BIG)
    speed_ev = Value(width=2, address=23, endian=Endian.BIG)
    special_ev = Value(width=2, address=25, endian=Endian.BIG)
    iv = Value(width=2, address=27, endian=Endian.BIG)
    pp = List(Value(width=1), 4, address=29)


class PartyMon(BoxMon):
    level = Value(width=1, address=33)
    box_level = Value(width=1, address=3)
    max_hp = Value(width=2, address=34, endian=Endian.BIG)
    attack = Value(width=2, address=36, endian=Endian.BIG)
    defense = Value(width=2, address=38, endian=Endian.BIG)
    speed = Value(width=2, address=40, endian=Endian.BIG)
    special = Value(width=2, address=42, endian=Endian.BIG)


class RedBlueEParty(Struct):
    _size = 0x194

    _count = Value(width=1, address=0)

    nicknames = List(Gen1StringE(11), 6, address=338)
    otNames = List(Gen1StringE(11), 6, address=272)
    pokemon = List(PartyMon(), 6, address=8)

    for i in xrange(6):
        pokemon[i].nickname = nicknames[i]
        pokemon[i].otName = otNames[i]

    def __len__(self):
        return self._count

    def __getitem__(self, index):
        if index >= self._count:
            raise IndexError
        return self.pokemon[index]


class RedBlueE(GBGame):
    roms = [{
        'size': 1048576,
        'crc32': 0x9F7FDD53,
        'md5': 0x3D45C1EE9ABD5738DF46D2BDDA8B57DC,
        'sha1': 0xEA9BCAE617FDF159B045185467AE58B2E4A48B9A
    }, {
        'size': 1048576,
        'crc32': 0xD6DA8A1A,
        'md5': 0x50927E843568814F7ED45EC4F944BD8B,
        'sha1': 0xD7037C83E1AE5B39BDE3C30787637BA1D4C48CE2
    }]

    party = RedBlueEParty(address=0xD163, segment=0)
