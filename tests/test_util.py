from gurtel.util import Url


class TestUrl(object):
    def equal(self, one, two):
        """
        For this test, want to ensure that compare-equal implies hash-equal.

        """
        return (one == two) and (hash(one) == hash(two))


    def test_no_qs(self):
        assert self.equal(
            Url("http://fake.base/path/"),
            Url("http://fake.base/path/"))


    def test_same_qs(self):
        assert self.equal(
            Url("http://fake.base/path/?foo=bar"),
            Url("http://fake.base/path/?foo=bar"))


    def test_different_key_order(self):
        assert self.equal(
            Url("http://fake.base/path/?foo=bar&arg=yo"),
            Url("http://fake.base/path/?arg=yo&foo=bar"))


    def test_different_value_order(self):
        assert not self.equal(
            Url("http://fake.base/path/?foo=bar&foo=yo"),
            Url("http://fake.base/path/?foo=yo&foo=bar"))


    def test_repr(self):
        assert self.equal(
            repr(Url("http://fake.base/path/?foo=bar")),
            "Url(http://fake.base/path/?foo=bar)")
