from typing import Tuple
from flask import request

def extrair_paginacao(default_per_page: int = 20, max_per_page: int = 100) -> Tuple[int, int, int, int]:
    """
    Extrai e valida os parâmetros 'page' e 'per_page' da query string.
    Retorna a tupla (page, per_page, start, end) para uso direto no .range(start, end) do PostgREST.
    """
    page_param = request.args.get("page", "1")
    per_page_param = request.args.get("per_page", str(default_per_page))

    try:
        page = int(page_param)
        if page < 1:
            page = 1
    except (ValueError, TypeError):
        page = 1

    try:
        per_page = int(per_page_param)
        if per_page < 1:
            per_page = default_per_page
        elif per_page > max_per_page:
            per_page = max_per_page
    except (ValueError, TypeError):
        per_page = default_per_page

    start = (page - 1) * per_page
    end = start + per_page - 1

    return page, per_page, start, end
