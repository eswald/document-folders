import collections
import environ
import logging


Path = environ.Path
log = logging.getLogger(__name__)


def boolean(value):
    val = str(value).lower()
    if val in {'true', 'on', 'yes', 'y', '1', 'ok'}:
        return True
    if val in {'false', 'off', 'no', 'n', '0', ''}:
        return False
    raise TypeError('Invalid boolean value %r' % (value,))


def directory(path):
    from os.path import abspath, isdir
    absolute_path = abspath(path)
    if not isdir(absolute_path):
        raise environ.ImproperlyConfigured("Missing path: {0}".format(absolute_path))
    return absolute_path


class Env(environ.Env):
    def get_value(self, var, cast=None, default=environ.Env.NOTSET, parse_default=False):
        try:
            return super().get_value(var, cast=cast, default=default, parse_default=parse_default)
        except TypeError as err:
            raise environ.ImproperlyConfigured('Invalid {cast} value for {var}'.format(cast=cast, var=var)) from err
    
    def bool(self, var, default=environ.Env.NOTSET):
        return self.get_value(var, cast=boolean, default=default)
    
    def directory(self, var, default=environ.Env.NOTSET):
        return self.get_value(var, cast=directory, default=default)
    
    def first(self, *varnames, cast=None, default=environ.Env.NOTSET):
        """Return the first of the given environment variables.
        """
        
        unset = environ.NoValue()
        for var in varnames:
            value = self.get_value(var, cast=cast, default=unset)
            if value is not unset:
                break
        else:
            if default is self.NOTSET:
                error_msg = "Set the {0} environment variable".format(varnames[0])
                raise ImproperlyConfigured(error_msg)
            
            value = default
        
        return value
    
    def secret(self, var):
        result = self.get_value(var, default=None)
        if result is None:
            import random
            import string
            log.warn('Constructing a new secret for %s', var)
            result = ''.join(random.choice(string.printable) for i in range(50))
        return result


class AlphabetContainer(collections.defaultdict):
    def __init__(self, env):
        self.env = env
    
    def __missing__(self, key):
        value = self.env.str('ENCODER_ALPHABET_' + key, default=None)
        if value is None:
            from .idencoder import random_alphabet
            value = random_alphabet()
            log.warning('Constructing a new alphabet for %s: %s', key, value)
        self[key] = value
        return value
