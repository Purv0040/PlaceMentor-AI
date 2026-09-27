from typing import List, TypeVar, Dict, Any

T = TypeVar("T")


def paginate(items: List[T], page: int = 1, size: int = 10) -> Dict[str, Any]:
    total = len(items)
    pages = (total + size - 1) // size if size > 0 else 1
    start = (page - 1) * size
    end = start + size
    return {
        "items": items[start:end],
        "total": total,
        "page": page,
        "size": size,
        "pages": pages,
    }
