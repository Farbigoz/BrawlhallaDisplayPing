import os
import re
from typing import Union

__all__ = ["ConfigFile", "ConfigElement"]
_type = type

END_STRING = ";\t\n"


class ConfigFileMeta(type):
    def __new__(metacls, cls, bases, classdict):
        if bases:
            classdict["_elements"] = {}
            for name, element in classdict.items():
                if type(element) == ConfigElement:
                    classdict["_elements"][name] = element
                    if element.name is None:
                        element.name = name

                elif element == ConfigElement:
                    element = element()
                    classdict["_elements"][name] = element
                    classdict[name] = element
                    element.name = name

                elif type(element) in [int, str, list, dict] and \
                        name not in ["__module__", "__qualname__", "_elements"]:

                    element = ConfigElement(default=element)
                    classdict["_elements"][name] = element
                    classdict[name] = element
                    element.name = name

        return super().__new__(metacls, cls, bases, classdict)


class ConfigFile(metaclass=ConfigFileMeta):
    _elements: dict

    type_to_str = {
        bool: "bool",
        int: "int",
        str: "str",
        list: "list",
        dict: "dict",
    }

    str_to_type = {v: k for k, v in type_to_str.items()}

    def __init__(self, path):
        self._path = path

        # Create .cfg file
        if not os.path.exists(self._path):
            open(self._path, "w").close()

        new_elements = False

        # Load config by ConfigElements on child class
        with open(self._path, "r") as cfg:
            cfgContent = cfg.read()

            for element in self._elements.values():
                _attr = re.findall(
                    f' *?{element.name} *?\[ *?({self.type_to_str[element.type]}) *?\][ =]*(.*){END_STRING}',
                    cfgContent)

                if _attr:
                    attr_type = self.str_to_type[_attr[0][0]]

                    if _attr[0][1]:
                        attr: str = _attr[0][1]

                        if attr_type in [int]:
                            element.attr = int(attr)
                        elif attr_type in [bool]:
                            element.attr = True if attr.casefold() in ["true", "1"] else False
                        else:
                            element.attr = attr
                    else:
                        element.attr = None

                else:
                    new_elements = True

        if new_elements:
            self._write_all()

    def _write_all(self):
        with open(self._path, "w") as cfg:
            for element in self._elements.values():
                attr = element.attr
                attr_type = self.type_to_str[element.type]

                if attr is None:
                    cfg.write(f'{element.name}[{attr_type}]{END_STRING}')

                else:
                    if element.type in [int]:
                        attr = str(attr)
                    elif element.type in [bool]:
                        attr = str(attr)
                    else:
                        attr = str(attr)

                    cfg.write(f'{element.name}[{attr_type}] = {attr}{END_STRING}')

    def __setattr__(self, key, value):
        if key in self._elements:
            if self._elements[key].attr != value:
                element = self._elements[key]

                if element.type != type(value):
                    raise TypeError("Variable type does not match specified type")

                element.attr = value
                self._write_all()

        # elif not key.startswith("_"):
        #    if key not in self._elements:
        #        self._elements[key] = ConfigElement(key, value)
        #        super().__setattr__(key, self._elements[key])
        #    else:
        #        self._elements[key].attr = value
        #
        #    self._write_all()

        else:
            super().__setattr__(key, value)

    def __getattribute__(self, key):
        obj = object.__getattribute__(self, key)

        if type(obj) == ConfigElement:
            return obj.attr
        else:
            return obj

    def __repr__(self):
        return "<ConfigFile: [" + ", ".join([str(el) for el in self._elements.values()]) + "]>"

    def __str__(self):
        return self.__repr__()

    def __contains__(self, key):
        return key in self._elements

    def __getitem__(self, key, default=None):
        return getattr(self, key, default)



class ConfigElement:
    def __init__(self, name: str = None, default=None, type: Union[int, str, list, dict] = str):
        self.name = None if name is None else re.sub('[^A-Za-z0-9_]', '', name)
        self.type = _type(default) if default is not None else type
        self.attr = default

    def __str__(self):
        return f"<ConfigElement: (name={self.name}, type={self.type}, attr={self.attr})>"
