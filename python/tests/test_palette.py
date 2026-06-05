import arknights_palette as akp
from arknights_palette.palette import _rgb_to_lab


def test_palette_lookup():
    assert "伊内丝" in akp.names()
    assert "CONFESS-47" in akp.names()
    assert "CONFESS-47" not in akp.names(rarity=6)
    assert len(akp.palette("伊内丝", 6)) == 6
    assert len(akp.palette("CONFESS-47", 6)) == 6
    assert len(akp.sequential("伊内丝", 16)) == 16
    assert len(akp.diverging("伊内丝", 17)) == 17


def test_themed_subtype_colors():
    subtype_map = {
        "immune": ["T cell", "B cell", "Macrophage"],
        "epithelial": ["AT1", "AT2"],
    }
    group_operator = {
        "immune": "浊心斯卡蒂",
        "epithelial": "塑心",
    }
    colors = akp.themed_subtype_colors(subtype_map, group_operator)
    assert set(colors) == {"T cell", "B cell", "Macrophage", "AT1", "AT2"}
    assert len(set(colors.values())) == 5


def test_arkplatte_aliases():
    assert akp.arkplatte("伊内丝", 4) == akp.palette("伊内丝", 4)
    assert akp.arkplatte_seq("伊内丝", 8) == akp.sequential("伊内丝", 8)
    assert akp.arkplatte_div("伊内丝", 9) == akp.diverging("伊内丝", 9)
    assert len(akp.arkplatte_cat(4)) == 4
    assert "伊内丝" in akp.arkplatte_names()
    assert akp.arkplatte_info("伊内丝")["name_cn"] == "伊内丝"


def test_scientific_colormap_shape():
    seq = akp.arkplatte_seq("浊心斯卡蒂", 9)
    seq_l = [_rgb_to_lab(color)[0] for color in seq]
    assert all(left >= right for left, right in zip(seq_l, seq_l[1:]))

    div = akp.arkplatte_div("浊心斯卡蒂", 9)
    div_l = [_rgb_to_lab(color)[0] for color in div]
    center = div_l[len(div_l) // 2]
    assert center > max(div_l[0], div_l[-1])
    assert abs(div_l[0] - div_l[-1]) < 4
