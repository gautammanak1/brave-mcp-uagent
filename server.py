import os
import time
import requests
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check for API key
BRAVE_API_KEY = os.getenv("BRAVE_API_KEY")
if not BRAVE_API_KEY:
    raise ValueError("BRAVE_API_KEY environment variable is required")

# Rate limiting configuration
RATE_LIMIT = {"per_second": 1, "per_month": 15000}
request_count = {"second": 0, "month": 0, "last_reset": time.time()}

def check_rate_limit():
    now = time.time()
    if now - request_count["last_reset"] > 1:
        request_count["second"] = 0
        request_count["last_reset"] = now
    if request_count["second"] >= RATE_LIMIT["per_second"] or request_count["month"] >= RATE_LIMIT["per_month"]:
        raise ValueError("Rate limit exceeded")
    request_count["second"] += 1
    request_count["month"] += 1

# Initialize MCP server
mcp = FastMCP("BraveSearch")

# Web search tool
@mcp.tool()
def brave_web_search(query: str, count: int = 10, offset: int = 0, result_type: str = "all", safety_level: str = "moderate", freshness: str = "all") -> str:
    """Performs a web search using the Brave Search API for general queries, news, articles, and online content.
    
    Supports pagination, result type filtering (web, news, videos), safety levels, and content freshness.
    Maximum 20 results per request, with offset for pagination.
    
    Args:
        query: Search query (max 400 chars, 50 words)
        count: Number of results (1-20, default 10)
        offset: Pagination offset (max 9, default 0)
        result_type: Result type to filter (web, news, videos, all; default all)
        safety_level: Content safety level (strict, moderate, off; default moderate)
        freshness: Content freshness (pd: past day, pw: past week, pm: past month, py: past year, all; default all)
    """
    check_rate_limit()

    # Validate inputs
    if len(query) > 400:
        raise ValueError("Query exceeds 400 characters")
    if count < 1 or count > 20:
        raise ValueError("Count must be between 1 and 20")
    if offset < 0 or offset > 9:
        raise ValueError("Offset must be between 0 and 9")
    valid_result_types = ["all", "web", "news", "videos"]
    if result_type not in valid_result_types:
        raise ValueError("Invalid result type")
    valid_safety_levels = ["strict", "moderate", "off"]
    if safety_level not in valid_safety_levels:
        raise ValueError("Invalid safety level")
    valid_freshness = ["all", "pd", "pw", "pm", "py"]
    if freshness not in valid_freshness:
        raise ValueError("Invalid freshness")

    url = "https://api.search.brave.com/res/v1/web/search"
    params = {
        "q": query,
        "count": count,
        "offset": offset,
        "safesearch": safety_level,
    }
    if result_type != "all":
        params["result_filter"] = result_type
    if freshness != "all":
        params["freshness"] = freshness

    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": BRAVE_API_KEY,
    }

    response = requests.get(url, params=params, headers=headers)
    if not response.ok:
        raise ValueError(f"Brave API error: {response.status_code} {response.text}")

    data = response.json()
    results = []
    if result_type in ["all", "web"] and data.get("web", {}).get("results"):
        results.extend([{"title": r["title"], "description": r["description"], "url": r["url"], "published": r.get("published", "")} for r in data["web"]["results"]])
    if result_type in ["all", "news"] and data.get("news", {}).get("results"):
        results.extend([{"title": r["title"], "description": r["description"], "url": r["url"], "published": r.get("published", "")} for r in data["news"]["results"]])
    if result_type in ["all", "videos"] and data.get("videos", {}).get("results"):
        results.extend([{"title": r["title"], "description": r["description"], "url": r["url"], "published": r.get("published", "")} for r in data["videos"]["results"]])

    if not results:
        return "No results found"

    return "\n\n".join(
        f"Title: {r['title']}\nDescription: {r['description']}\nURL: {r['url']}\n{'Published: ' + r['published'] if r['published'] else ''}"
        for r in results
    )

# Local search tool
@mcp.tool()
def brave_local_search(query: str, count: int = 5, safety_level: str = "moderate") -> str:
    """Searches for local businesses and places using Brave's Local Search API.
    
    Best for queries about physical locations, businesses, restaurants, or services.
    Returns detailed information including business names, addresses, ratings, phone numbers, and hours.
    Automatically falls back to web search if no local results are found.
    
    Args:
        query: Local search query (e.g., 'pizza near Central Park')
        count: Number of results (1-20, default 5)
        safety_level: Content safety level (strict, moderate, off; default moderate)
    """
    check_rate_limit()

    # Validate inputs
    if len(query) > 400:
        raise ValueError("Query exceeds 400 characters")
    if count < 1 or count > 20:
        raise ValueError("Count must be between 1 and 20")
    valid_safety_levels = ["strict", "moderate", "off"]
    if safety_level not in valid_safety_levels:
        raise ValueError("Invalid safety level")

    # Initial search for location IDs
    url = "https://api.search.brave.com/res/v1/web/search"
    params = {
        "q": query,
        "search_lang": "en",
        "result_filter": "locations",
        "count": count,
        "safesearch": safety_level,
    }
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": BRAVE_API_KEY,
    }

    response = requests.get(url, params=params, headers=headers)
    if not response.ok:
        raise ValueError(f"Brave API error: {response.status_code} {response.text}")

    data = response.json()
    location_ids = [r["id"] for r in data.get("locations", {}).get("results", []) if r.get("id")]

    if not location_ids:
        # Fallback to web search
        return brave_web_search(query, count, 0, "all", safety_level, "all")

    # Fetch POI details
    poi_url = "https://api.search.brave.com/res/v1/local/pois"
    poi_params = {"ids": location_ids}
    poi_response = requests.get(poi_url, params=poi_params, headers=headers)
    if not poi_response.ok:
        raise ValueError(f"Brave API error: {poi_response.status_code} {poi_response.text}")

    poi_data = poi_response.json()
    locations = poi_data.get("results", [])

    # Fetch descriptions
    desc_url = "https://api.search.brave.com/res/v1/local/descriptions"
    desc_response = requests.get(desc_url, params=poi_params, headers=headers)
    if not desc_response.ok:
        raise ValueError(f"Brave API error: {desc_response.status_code} {desc_response.text}")

    desc_data = desc_response.json().get("descriptions", {})

    # Format results
    results = []
    for loc in locations:
        address = ", ".join(
            filter(
                None,
                [
                    loc.get("address", {}).get("streetAddress", ""),
                    loc.get("address", {}).get("addressLocality", ""),
                    loc.get("address", {}).get("addressRegion", ""),
                    loc.get("address", {}).get("postalCode", ""),
                ],
            )
        ) or "N/A"
        result = f"""Name: {loc.get('name', 'N/A')}
Address: {address}
Phone: {loc.get('phone', 'N/A')}
Rating: {loc.get('rating', {}).get('ratingValue', 'N/A')} ({loc.get('rating', {}).get('ratingCount', 0)} reviews)
Price Range: {loc.get('priceRange', 'N/A')}
Hours: {', '.join(loc.get('openingHours', [])) or 'N/A'}
Description: {desc_data.get(loc.get('id'), 'No description available')}"""
        results.append(result)

    return "\n---\n".join(results) or "No local results found"

if __name__ == "__main__":
    mcp.run(transport="stdio")
