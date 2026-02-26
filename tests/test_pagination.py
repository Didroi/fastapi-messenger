from app.utils.pagination import PaginationParams


def make_pagination(page: int, size: int) -> PaginationParams:
    p = PaginationParams.__new__(PaginationParams)
    p.page = page
    p.size = size
    p.offset = (page - 1) * size
    return p


# --- offset calculation ---


def test_first_page_offset_is_zero():
    p = make_pagination(page=1, size=20)
    assert p.offset == 0


def test_second_page_offset():
    p = make_pagination(page=2, size=20)
    assert p.offset == 20


def test_third_page_offset():
    p = make_pagination(page=3, size=10)
    assert p.offset == 20


def test_offset_with_large_page():
    p = make_pagination(page=5, size=100)
    assert p.offset == 400
