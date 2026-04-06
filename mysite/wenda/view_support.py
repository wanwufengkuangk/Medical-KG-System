import sys
from pathlib import Path

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
workspace_root_str = str(WORKSPACE_ROOT)
if workspace_root_str not in sys.path:
    sys.path.append(workspace_root_str)

import json


def is_ajax(request) -> bool:
    return request.headers.get("x-requested-with") == "XMLHttpRequest"


def json_http_response(payload) -> HttpResponse:
    return HttpResponse(json.dumps(payload, ensure_ascii=False), content_type="application/json")


def slice_page(items, page: int, page_size: int):
    start = page * page_size
    end = min((page + 1) * page_size, len(items))
    return items[start:end]


def get_graph():
    from Neo4j.config import graph

    return graph
