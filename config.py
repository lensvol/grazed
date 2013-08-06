#coding: utf-8

import ConfigParser


class Config(object):

    def __init__(self, *files, **options):
        defaults = options.pop('defaults', {})
        self.cfg_parser = ConfigParser.ConfigParser(defaults)

        for fn in files:
            if fn:
                self.cfg_parser.read(fn)

    def get_value(self, section, field):
        val = None

        try:
            val = self.cfg_parser.get(section, field)
        except ConfigParser.NoSectionError:
            val = None
        except ConfigParser.NoOptionError:
            val = None

        return val
