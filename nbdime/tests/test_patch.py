# coding: utf-8

# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

from __future__ import unicode_literals

from nbdime import patch
from nbdime.diff_format import make_op, Diff


# TODO: Check and improve test coverage
# TODO: Add tests for invalid input and error handling
# TODO: Add more corner cases (combinations of delete-then-add etc.)


def test_patch_str():
    # Test +, single item insertion
    assert patch("42", [make_op(Diff.ADD, 0, "3"), make_op(Diff.REMOVE, 1)]) == "34"

    # Test -, single item deletion
    assert patch("3", [make_op(Diff.REMOVE, 0)]) == ""
    assert patch("42", [make_op(Diff.REMOVE, 0)]) == "2"
    assert patch("425", [make_op(Diff.REMOVE, 0)]) == "25"
    assert patch("425", [make_op(Diff.REMOVE, 1)]) == "45"
    assert patch("425", [make_op(Diff.REMOVE, 2)]) == "42"

    # Test :, single item replace
    assert patch("52", [make_op(Diff.REPLACE, 0, "4")]) == "42"
    assert patch("41", [make_op(Diff.REPLACE, 1, "2")]) == "42"
    assert patch("42", [make_op(Diff.REPLACE, 0, "3"), make_op(Diff.REPLACE, 1, "5")]) == "35"
    assert patch("hello", [make_op(Diff.REPLACE, 0, "H")]) == "Hello"
    # Replace by delete-then-insert
    assert patch("world", [make_op(Diff.REMOVE, 0), make_op(Diff.ADD, 0, "W")]) == "World"

    # Test !, item patch (doesn't make sense for str)
    pass

    # Test ++, sequence insertion
    assert patch("", [make_op(Diff.ADDRANGE, 0, "34"), make_op(Diff.ADD, 0, "5"), make_op(Diff.ADDRANGE, 0, "67")]) == "34567"

    # Test --, sequence deletion
    assert patch("abcd", [make_op(Diff.REMOVERANGE, 0, 2)]) == "cd"
    assert patch("abcd", [make_op(Diff.REMOVERANGE, 1, 2)]) == "ad"
    assert patch("abcd", [make_op(Diff.REMOVERANGE, 2, 2)]) == "ab"


def test_patch_list():
    # Test +, single item insertion
    assert patch([], [make_op(Diff.ADD, 0, 3)]) == [3]
    assert patch([], [make_op(Diff.ADD, 0, 3), make_op(Diff.ADD, 0, 4)]) == [3, 4]
    assert patch([], [make_op(Diff.ADD, 0, 3), make_op(Diff.ADD, 0, 4), make_op(Diff.ADD, 0, 5)]) == [3, 4, 5]

    # Test -, single item deletion
    assert patch([3], [make_op(Diff.REMOVE, 0)]) == []
    assert patch([5, 6, 7], [make_op(Diff.REMOVE, 0)]) == [6, 7]
    assert patch([5, 6, 7], [make_op(Diff.REMOVE, 1)]) == [5, 7]
    assert patch([5, 6, 7], [make_op(Diff.REMOVE, 2)]) == [5, 6]
    assert patch([5, 6, 7], [make_op(Diff.REMOVE, 0), make_op(Diff.REMOVE, 2)]) == [6]

    # Test :, single item replace
    pass

    # Test !, item patch
    assert patch(["hello", "world"], [make_op(Diff.PATCH, 0, [make_op(Diff.REPLACE, 0, "H")]),
                                      make_op(Diff.PATCH, 1, [make_op(Diff.REMOVE, 0), make_op(Diff.ADD, 0, "W")])]) == ["Hello", "World"]

    # Test ++, sequence insertion
    assert patch([], [make_op(Diff.ADDRANGE, 0, [3, 4]), make_op(Diff.ADD, 0, 5), make_op(Diff.ADDRANGE, 0, [6, 7])]) == [3, 4, 5, 6, 7]

    # Test --, sequence deletion
    assert patch([5, 6, 7, 8], [make_op(Diff.REMOVERANGE, 0, 2)]) == [7, 8]
    assert patch([5, 6, 7, 8], [make_op(Diff.REMOVERANGE, 1, 2)]) == [5, 8]
    assert patch([5, 6, 7, 8], [make_op(Diff.REMOVERANGE, 2, 2)]) == [5, 6]


def test_patch_dict():
    # Test +, single item insertion
    assert patch({}, [make_op(Diff.ADD, "d", 4)]) == {"d": 4}
    assert patch({"a": 1}, [make_op(Diff.ADD, "d", 4)]) == {"a": 1, "d": 4}

    #assert patch({"d": 1}, [make_op(Diff.ADD, "d", 4)]) == {"d": 4} # currently triggers assert, raise exception or allow?

    # Test -, single item deletion
    assert patch({"a": 1}, [make_op(Diff.REMOVE, "a")]) == {}
    assert patch({"a": 1, "b": 2}, [make_op(Diff.REMOVE, "a")]) == {"b": 2}

    # Test :, single item replace
    assert patch({"a": 1, "b": 2}, [make_op(Diff.REPLACE, "a", 3)]) == {"a": 3, "b": 2}
    assert patch({"a": 1, "b": 2}, [make_op(Diff.REPLACE, "a", 3), make_op(Diff.REPLACE, "b", 5)]) == {"a": 3, "b": 5}

    # Test !, item patch
    subdiff = [make_op(Diff.PATCH, 0, [make_op(Diff.REPLACE, 0, "H")]), make_op(Diff.PATCH, 1, [make_op(Diff.REMOVE, 0), make_op(Diff.ADD, 0, "W")])]
    assert patch({"a": ["hello", "world"], "b": 3}, [make_op(Diff.PATCH, "a", subdiff)]) == {"a": ["Hello", "World"], "b": 3}
