import sys
import venusian
import mgba_gamedata
from mgba_gamedata.types import Struct, StructType


class Registry(object):
    def __init__(self):
        self.platforms = {}
        self.scanned = False

    def add(self, name, klass):
        self.platforms[name].add(klass)

    def addPlatform(self, name, platform):
        self.platforms[name] = platform()

    def scan(self):
        if self.scanned:
            return
        scanner = venusian.Scanner(registry=self)
        scanner.scan(mgba_gamedata, categories=('platform', 'game'))
        self.scanned = True

    def search(self, platform, info):
        if not self.scanned:
            self.scan()
        return self.platforms[platform].search(info)


class GameType(StructType):
    def __new__(cls, name, bases, attrs):
        klass = super(GameType, cls).__new__(cls, name, bases, attrs)
        platform = None
        if 'platform' in attrs:
            platform = attrs['platform']
        else:
            for base in bases:
                if hasattr(base, 'platform'):
                    platform = base.platform
        if platform:
            venusian.attach(klass, GameType.callback, category='game')
        return klass

    @staticmethod
    def callback(scanner, name, klass):
        scanner.registry.add(klass.platform.__name__, klass)


class RegisterPlatform(type):
    def __new__(cls, name, bases, attrs):
        klass = super(RegisterPlatform, cls).__new__(cls, name, bases, attrs)
        venusian.attach(klass, RegisterPlatform.callback, category='platform')
        return klass

    @staticmethod
    def callback(scanner, name, klass):
        scanner.registry.addPlatform(name, klass)


class Platform(object):
    __metaclass__ = RegisterPlatform

    def __init__(self):
        self.crc32 = {}
        self.md5 = {}
        self.sha1 = {}
        self.sha256 = {}

    def add(self, klass):
        for rom in getattr(klass, 'roms', []):
            if 'crc32' in rom:
                self.crc32[rom['crc32']] = klass
            if 'md5' in rom:
                self.md5[rom['md5']] = klass
            if 'sha1' in rom:
                self.sha1[rom['sha1']] = klass
            if 'sha256' in rom:
                self.sha256[rom['sha256']] = klass

    def search(self, info):
        item = None
        for hash in ('sha256', 'sha1', 'md5', 'crc32'):
            if hash in info:
                test_item = getattr(self, hash).get(info[hash])
                if test_item:
                    if not item:
                        item = test_item
                    elif item != test_item:
                        return None
        return item


class Game(Struct):
    __metaclass__ = GameType

    _memory = None

    def __init__(self, memory=None):
        super(Game, self).__init__()
        self.instantiate(memory)
