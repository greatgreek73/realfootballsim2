import pytest

from transfers.templatetags.transfer_tags import get_item


def test_get_item_returns_value_or_none():
    data = {"a": 1, "b": 2}
    assert get_item(data, "a") == 1
    assert get_item(data, "missing") is None
