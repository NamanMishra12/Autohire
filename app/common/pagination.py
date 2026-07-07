from math import ceil


def paginate(total: int, page: int, page_size: int):

    return {
        "page": page,
        "page_size": page_size,
        "total_records": total,
        "total_pages": ceil(total / page_size),
    }