"Django-compatible disk and file backed cache."

from django.core.cache.backends.base import DEFAULT_TIMEOUT, BaseCache

from .fanout import FanoutCache


class DjangoCache(BaseCache):
    "Django-compatible disk and file backed cache."
    def __init__(self, directory, params):
        """Initialize DjangoCache instance.

        :param str directory: cache directory
        :param dict params: cache parameters

        """
        super(DjangoCache, self).__init__(params)
        shards = params.get('SHARDS', 8)
        timeout = params.get('DATABASE_TIMEOUT', 0.025)
        options = params.get('OPTIONS', {})
        self._cache = FanoutCache(
            directory, shards=shards, timeout=timeout, **options
        )


    def add(self, key, value, timeout=DEFAULT_TIMEOUT, version=None,
            read=False, tag=None):
        # pylint: disable=arguments-differ
        if self.has_key(key, version):
            return False
        return self.set(
            key, value, timeout=timeout, version=version, read=read, tag=tag
        )

    add.__doc__ = BaseCache.add.__doc__


    def get(self, key, default=None, version=None, read=False,
            expire_time=False, tag=False):
        # pylint: disable=arguments-differ
        key = self.make_key(key, version=version)
        return self._cache.get(
            key, default=default, read=read, expire_time=expire_time, tag=tag
        )

    get.__doc__ = BaseCache.get.__doc__


    def set(self, key, value, timeout=DEFAULT_TIMEOUT, version=None,
            read=False, tag=None):
        # pylint: disable=arguments-differ
        key = self.make_key(key, version=version)
        timeout = self.get_backend_timeout(timeout=timeout)
        return self._cache.set(key, value, expire=timeout, read=read, tag=tag)

    set.__doc__ = BaseCache.set.__doc__


    def delete(self, key, version=None):
        key = self.make_key(key, version=version)
        self._cache.delete(key)

    delete.__doc__ = BaseCache.delete.__doc__


    def has_key(self, key, version=None):
        key = self.make_key(key, version=version)
        return key in self._cache

    has_key.__doc__ = BaseCache.has_key.__doc__


    def clear(self):
        self._cache.clear()

    clear.__doc__ = BaseCache.clear.__doc__


    def close(self):
        self._cache.close()

    close.__doc__ = BaseCache.close.__doc__


    def get_backend_timeout(self, timeout=DEFAULT_TIMEOUT):
        """Return seconds to expiration.

        :param float timeout: seconds to expire (default `DEFAULT_TIMEOUT`)

        """
        if timeout == DEFAULT_TIMEOUT:
            timeout = self.default_timeout
        elif timeout == 0:
            # ticket 21147 - avoid time.time() related precision issues
            timeout = -1
        return None if timeout is None else timeout
