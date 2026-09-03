import importlib.util
from pathlib import Path


def load_router():
    path = Path(__file__).with_name("search_router.py")
    spec = importlib.util.spec_from_file_location("search_router", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_get_contract_aliases():
    payload = load_router().search_payload_from_query(
        "/search?q=OpenAI+revenue&numResults=7&page=2&lang=es"
    )
    assert payload == {"query": "OpenAI revenue", "limit": "7", "page": "2", "lang": "es"}


def test_v2_contract_defaults():
    payload = load_router().search_payload_from_query("/v2/search?query=Firecrawl&limit=3")
    assert payload == {"query": "Firecrawl", "limit": "3", "page": 1}
