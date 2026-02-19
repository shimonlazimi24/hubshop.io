import pytest

from backend.utils.pagination import PaginatedResult, PaginationParams


@pytest.mark.unit
class TestPagination:
    def test_offset_calculation(self) -> None:
        assert PaginationParams(page=1, page_size=20).offset == 0
        assert PaginationParams(page=2, page_size=20).offset == 20
        assert PaginationParams(page=3, page_size=10).offset == 20

    def test_total_pages(self) -> None:
        assert PaginatedResult(items=[], total=0, page=1, page_size=20).total_pages == 0
        assert PaginatedResult(items=[], total=1, page=1, page_size=20).total_pages == 1
        assert PaginatedResult(items=[], total=20, page=1, page_size=20).total_pages == 1
        assert PaginatedResult(items=[], total=21, page=1, page_size=20).total_pages == 2
        assert PaginatedResult(items=[], total=100, page=1, page_size=10).total_pages == 10
