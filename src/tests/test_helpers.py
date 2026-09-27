import pytest

from cell_sandbox.helpers import ascii2tuple, has_any_flag, normalize_value

class TestAscii2vec:
    def test_ascii2vec_returns_location_of_single_hash(self):
        assert ascii2tuple("#") == [(0,0)]

    def test_ascii2vec_strips_witespace(self):
        assert ascii2tuple("  #  ") == [(0,0)]

    def test_ascii2vec_strips_newlines(self):
        assert ascii2tuple("\n#\n") == [(0,0)]

    def test_ascii2vec_strips_newlines_and_spaces(self):
        assert ascii2tuple("\n # \n") == [(0,0)]

    def test_ascii2vec_strips_whitespace_on_each_line(self):
        assert ascii2tuple("   #   \n   #   \n   #   ") == [(0,-1),(0,0),(0,1)]

    def test_ascii2vec_centers_horizontally(self):
        assert ascii2tuple("###") == [(-1,0),(0,0),(1,0)]

    def test_ascii2vec_centers_vertically(self):
        assert ascii2tuple("#\n#\n#") == [(0,-1),(0,0),(0,1)]

    def test_ascii2vec_centers(self):
        assert ascii2tuple("###\n###\n###") == [
            (-1,-1),(0,-1),(1,-1),
            (-1,0),(0,0),(1,0),
            (-1,1),(0,1),(1,1),
        ]

    def test_glider(self):
        glider = """
            .#.
            ..#
            ###
        """
        assert ascii2tuple(glider) == [
                   (0,-1),
                          (1, 0),
           (-1, 1),(0, 1),(1, 1),
        ]


def test_has_any_flags():
    assert has_any_flag(0b01, 0b01), "0b01 contains 0b01"
    assert has_any_flag(0b01, 0b10, 0b01), "0b01 contains 0b10 or 0b01"
    assert has_any_flag(0b11, 0b10, 0b01), "0b11 contains 0b10 or 0b01"
    assert has_any_flag(0b11, 0b10), "0b11 contains 0b10"
    assert has_any_flag(0b11, 0b01), "0b11 contains 0b01"
    assert not has_any_flag(0b01, 0b10), "0b01 does not contains 0b10"
    assert not has_any_flag(0b01, 0b10, 0b100), "0b01 does not contains 0b10 or 0b100"
    assert not has_any_flag(0b11, 0b100, 0b1000), "0b11 does not contains 0b100 or 0b1000"

def test_normalize_value():
    assert normalize_value(50, 0, 100) == 0.5

