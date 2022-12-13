from collections import OrderedDict
from configupdater import ConfigUpdater
import configparser

class multidict(OrderedDict):
    _unique = 0   # class variable

    def __setitem__(self, key, val):
     if isinstance(val, dict):
         self._unique += 1
         key += str(self._unique)
     OrderedDict.__setitem__(self, key, val)
# 这种方法貌似不怎么好用,而且读进来的不在缓存中
Config = configparser.ConfigParser(defaults=None, dict_type=multidict, strict=False)
Config.read(r"xxx.ini")

# configupdater支持重复的sections,但是获取时还是要预先知道里面的key才能搞定
updater = ConfigUpdater(strict=False, space_around_delimiters=False)
updater.read(r"xxx.ini")
for i in updater.iter_sections():
    try:
        SoftBin = str(i['xxx']).strip().split("=")[-1]
        SoftBinDesc = str(i['xxx']).strip().split("=")[-1]
        SoftBinDescs[SoftBin] = SoftBinDesc
    except Exception:
        pass
