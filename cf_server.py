"""MCP server exposing a single tool, get_problem, backed by the official
Codeforces API (codeforces.com/api/problemset.problems). Stdio transport.

Never write to stdout: it is the MCP transport channel. All logging goes to
stderr only.
"""

import logging
import random
import sys

import requests
from mcp.server.fastmcp import FastMCP

logging.basicConfig(
    level=logging.INFO,
    stream=sys.stderr,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("cf_server")

CODEFORCES_API_URL = "https://codeforces.com/api/problemset.problems"

mcp = FastMCP("cf-problems")


@mcp.tool()
def get_problem(tags: list[str], min_rating: int = 800, max_rating: int = 3500) -> dict:
    """Fetch a real Codeforces problem matching the given tags and rating range.

    Args:
        tags: Codeforces problem tags to match, e.g. ["dp"], ["graphs", "dfs and similar"].
              All tags must be present on a problem to match (Codeforces AND semantics).
        min_rating: Minimum problem rating (inclusive). Problems with no rating are skipped.
        max_rating: Maximum problem rating (inclusive).

    Returns:
        A dict with the matched problem (name, contestId, index, rating, tags, url),
        or an "error" key if no problem matched or the API call failed.
    """
    params = {}
    if tags:
        params["tags"] = ";".join(tags)

    logger.info("Fetching problems for tags=%s rating=[%s,%s]", tags, min_rating, max_rating)

    try:
        resp = requests.get(CODEFORCES_API_URL, params=params, timeout=15)
        resp.raise_for_status()
        payload = resp.json()
    except requests.RequestException as exc:
        logger.error("Codeforces API request failed: %s", exc)
        return {"error": f"Codeforces API request failed: {exc}"}

    if payload.get("status") != "OK":
        logger.error("Codeforces API returned non-OK status: %s", payload)
        return {"error": "Codeforces API returned an error status"}

    problems = payload["result"]["problems"]
    matched = [
        p
        for p in problems
        if p.get("rating") is not None and min_rating <= p["rating"] <= max_rating
    ]

    if not matched:
        logger.info("No problems matched tags=%s rating=[%s,%s]", tags, min_rating, max_rating)
        return {"error": "No problem found matching those tags and rating range"}

    problem = random.choice(matched)
    contest_id = problem["contestId"]
    index = problem["index"]

    return {
        "name": problem["name"],
        "contestId": contest_id,
        "index": index,
        "rating": problem["rating"],
        "tags": problem["tags"],
        "url": f"https://codeforces.com/contest/{contest_id}/problem/{index}",
    }


if __name__ == "__main__":
    mcp.run()
