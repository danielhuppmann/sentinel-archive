import pytest
import requests

from sark.metatools import ODLS


@pytest.mark.parametrize(
    "http_cache", [ODLS], indirect=["http_cache"],
)
def test_http_cache_file(http_cache):
    assert http_cache.cachedir.exists()
    assert http_cache.cachefile("foo")[0] == http_cache.cachefile("foo")[0]
    assert http_cache.cachefile("foo")[0] != http_cache.cachefile("bar")[0]


@pytest.mark.parametrize(
    "http_cache", [ODLS], indirect=["http_cache"],
)
def test_http_cache_fetch(http_cache):
    grp = "all"
    contents = http_cache.fetch(http_cache.cachefile(grp)[1])
    assert contents
    assert isinstance(contents, bytes)
    assert not http_cache.cachefile(grp)[0].exists()  # cache not created


# incorrect url
@pytest.mark.parametrize(
    "http_cache", [ODLS[:-1]], indirect=["http_cache"],
)
def test_http_cache_fetch_bad_url(caplog, http_cache):
    grp = "all"
    with pytest.raises(ValueError, match=f"error: {ODLS[:-1]} ".format(grp)):
        http_cache.fetch(http_cache.cachefile(grp)[1])


# non-existent domain / no network
@pytest.mark.parametrize(
    "http_cache", ["https://iamnota.site/{}"], indirect=["http_cache"],
)
def test_http_cache_fetch_no_conn(http_cache):
    grp = "all"
    with pytest.raises(requests.ConnectionError):
        http_cache.fetch(http_cache.cachefile(grp)[1])


@pytest.mark.parametrize(
    "http_cache", [ODLS], indirect=["http_cache"],
)
def test_http_cache_get(http_cache):
    grp = "all"
    contents = http_cache.get(grp)
    assert contents
    assert isinstance(contents, bytes)
    assert http_cache.cachefile(grp)[0].exists()  # cache created


@pytest.mark.parametrize(
    "http_cache", [ODLS], indirect=["http_cache"],
)
def test_http_cache_many_gets(http_cache):
    grps = ["all", "osi"]
    contents, caches = [], []
    for grp in grps:
        contents += [http_cache.get(grp)]
        caches += [http_cache.cachefile(grp)[0]]

    assert contents[0] != contents[1]
    assert caches[0] != caches[1]
    assert caches[0].read_bytes() != caches[1].read_bytes()


@pytest.mark.parametrize(
    "http_cache", [ODLS], indirect=["http_cache"],
)
def test_http_cache_remove(http_cache):
    def _cache_file(count: int):
        caches = tuple(
            http_cache.cachedir.glob(f"http-{http_cache.url_t_hex}-*")
        )
        assert len(caches) == count

    n = len(tuple(map(http_cache.get, ["all", "osi", "od"])))
    _cache_file(n)

    http_cache.remove("all")  # remove one
    _cache_file(n - 1)

    http_cache.remove()  # remove the rest
    _cache_file(0)

    with pytest.raises(FileNotFoundError):
        http_cache.remove("not-there")
