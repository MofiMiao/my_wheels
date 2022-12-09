from collections import OrderedDict
import configparser

class multidict(OrderedDict):
     _unique = 0   # class variable

     def __setitem__(self, key, val):
         if isinstance(val, dict):
             self._unique += 1
             key += str(self._unique)
         OrderedDict.__setitem__(self, key, val)

 Config = configparser.ConfigParser(defaults=None, dict_type=multidict, strict=False)

 Config.read(r"xxx.ini")
