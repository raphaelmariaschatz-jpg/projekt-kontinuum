#!/usr/bin/env python3
"""Low-volume discovery connector for global public knowledge APIs."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request


TIMEOUT = 30
DEFAULT_LIMIT = 10
USER_AGENT = os.getenv(
    "KONTINUUM_USER_AGENT",
    "ProjektKontinuum/23.0 (configure KONTINUUM_USER_AGENT with a contact address)",
)


def get_json(url: str, params: dict[str, str | int]) -> object:
    query = urllib.parse.urlencode(params)
    request = urllib.request.Request(
        f"{url}?{query}",
        headers={"Accept": "application/json", "User-Agent": USER_AGENT},
    )
    with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
        return json.load(response)


def search_ror(query: str, limit: int) -> object:
    data = get_json("https://api.ror.org/v2/organizations", {"query": query})
    if isinstance(data, dict) and isinstance(data.get("items"), list):
        data["items"] = data["items"][:limit]
    return data


def search_openalex(entity: str, query: str, limit: int) -> object:
    api_key = os.getenv("OPENALEX_API_KEY")
    if not api_key:
        raise RuntimeError("OPENALEX_API_KEY is required by OpenAlex.")
    return get_json(
        f"https://api.openalex.org/{entity}",
        {"search": query, "per-page": limit, "api_key": api_key},
    )


def search_crossref(query: str, limit: int) -> object:
    params: dict[str, str | int] = {"query": query, "rows": limit}
    mailto = os.getenv("CROSSREF_MAILTO")
    if mailto:
        params["mailto"] = mailto
    return get_json("https://api.crossref.org/works", params)


def search_datacite(query: str, limit: int) -> object:
    return get_json("https://api.datacite.org/dois", {"query": query, "page[size]": limit})


def search_zenodo(query: str, limit: int) -> object:
    return get_json("https://zenodo.org/api/records", {"q": query, "size": limit})


def search_lectures(query: str, limit: int) -> object:
    archive_query = f"({query}) AND mediatype:(movies OR audio)"
    return get_json(
        "https://archive.org/advancedsearch.php",
        {
            "q": archive_query,
            "fl[]": "identifier,title,creator,date,description,subject",
            "rows": limit,
            "output": "json",
        },
    )


def search_open_library(query: str, limit: int) -> object:
    return get_json(
        "https://openlibrary.org/search.json",
        {"q": query, "limit": limit, "fields": "key,title,author_name,first_publish_year,isbn"},
    )


def search_loc(query: str, limit: int) -> object:
    return get_json("https://www.loc.gov/search/", {"q": query, "fo": "json", "c": limit})


def search_wikidata(query: str, limit: int) -> object:
    return get_json(
        "https://www.wikidata.org/w/api.php",
        {
            "action": "wbsearchentities",
            "search": query,
            "language": "en",
            "uselang": "en",
            "format": "json",
            "limit": limit,
        },
    )


SEARCHERS = {
    "universities": search_ror,
    "organizations": search_ror,
    "publications": search_crossref,
    "research-outputs": search_datacite,
    "presentations": search_zenodo,
    "lectures": search_lectures,
    "books": search_open_library,
    "library-catalog": search_loc,
    "public-libraries": search_wikidata,
    "linked-open-data": search_wikidata,
    "scientists": lambda query, limit: search_openalex("authors", query, limit),
    "scholarly-works": lambda query, limit: search_openalex("works", query, limit),
    "research-institutions": lambda query, limit: search_openalex("institutions", query, limit),
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("category", choices=sorted(SEARCHERS))
    parser.add_argument("query")
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    args = parser.parse_args()
    limit = max(1, min(args.limit, 100))

    try:
        result = SEARCHERS[args.category](args.query, limit)
    except (RuntimeError, urllib.error.URLError, TimeoutError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
