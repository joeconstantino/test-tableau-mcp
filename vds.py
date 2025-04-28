"""
Simple MCP wrapper around Tableau VizQL Data Service, written in the same
style as the “weather” sample provided.

Run with uv --directory <path> run vds.py

The Claude Desktop entry in settings.json would then point `command` at
`uv` and `args` at ["run", "--directory", "/ABS/PATH/TO/PROJECT", "server.py"].
"""
from __future__ import annotations

from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

# ────────────────────────────────────────────────────────────────────────────────
# FastMCP initialization
# ────────────────────────────────────────────────────────────────────────────────
mcp = FastMCP("vizql-data-service")

# ────────────────────────────────────────────────────────────────────────────────
# Constants
# ────────────────────────────────────────────────────────────────────────────────
# Use the exact prefix you verified via curl/DevTools:
VIZQL_API_BASE = (
    "" #Add your Tableau server URL (i.e https://test.awsquickstart.tableau.com)
    "/api/v1/vizql-data-service" #VDS service endpoint
)

METADATA_GRAPHQL = (
    "" #Add your Tableau server URL (i.e https://test.awsquickstart.tableau.com)
    "/api/metadata/graphql" #metadata api endpoint
)

USER_AGENT = "vizql-mcp/1.0"

# Hard‑wire a test datasource LUID
DS_LUID = ""


OPTIONS = {
    "returnFormat": "OBJECTS",
    "debug": False,
    "disaggregate": False,
}

#hardcode a valid session token
AUTH_TOKEN = ""
# ────────────────────────────────────────────────────────────────────────────────


# ────────────────────────────────────────────────────────────────────────────────
# Helper functions for VizQL Data Service and metadata api requests
# ────────────────────────────────────────────────────────────────────────────────
async def make_vizql_request(
    path: str,
    *,
    method: str = "GET",
    body: dict[str, Any] | None = None,
    auth_token: str | None = None,
) -> dict[str, Any] | None:
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    token = auth_token or AUTH_TOKEN
    if token:
        headers["X-Tableau-Auth"] = token

    url = f"{VIZQL_API_BASE}/{path.lstrip('/')}"
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.request(
                method,
                url,
                json=body,
                headers=headers,
                timeout=10.0,
            )
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as e:
            return {"error": "VizQL request failed", "status": e.response.status_code, "detail": e.response.text}
        except Exception as exc:
            return {"error": "VizQL request failed", "detail": str(exc)}

def get_datasource_query(luid: str) -> str:
    return f"""
    query Datasources {{
      publishedDatasources(filter: {{ luid: \"{luid}\" }}) {{
        name
        description
        datasourceFilters {{ field {{ name description }} }}
        fields {{ name description }}
      }}
    }}
    """
# ────────────────────────────────────────────────────────────────────────────────
# MCP Tool Definitions
# ────────────────────────────────────────────────────────────────────────────────
@mcp.tool()
async def query_datasource(query: dict[str, Any]) -> Any:
    """
    Run a Tableau VizQL query.

    Args:
        query: *Only* the `query` part of the VizQL payload, e.g.
               {
                   "fields": [...],
                   "filters": [...]
               }
    All other fields are injected automatically by the tool.
    """
    if not AUTH_TOKEN:
        return "Server mis‑configured: get a valid session token."

    payload = {"datasource": {"datasourceLuid": DS_LUID}, "query": query, "options": OPTIONS}
    return await make_vizql_request("query-datasource", method="POST", body=payload)

@mcp.tool()
async def list_fields() -> Any:
    """
    Fetches field metadata (name, description) for the hard-wired datasource
    via Tableau's Metadata API, reusing the shared get_datasource_query function.
    Returns a list of field dicts or an error message.
    """
    if not AUTH_TOKEN:
        return "Error: TABLEAU_PAT environment variable is not set."

    query = get_datasource_query(DS_LUID)
    body = {"query": query}

    async with httpx.AsyncClient() as client:
        try:
            headers = {"Content-Type": "application/json", "X-Tableau-Auth": AUTH_TOKEN}
            resp = await client.post(METADATA_GRAPHQL, headers=headers, json=body, timeout=20.0)
            resp.raise_for_status()
            result = resp.json()
        except httpx.HTTPStatusError as e:
            return {"error": "Metadata API HTTP error", "status": e.response.status_code, "detail": e.response.text}
        except Exception as exc:
            return {"error": "Metadata API request failed", "detail": str(exc)}

    if result.get("errors"):
        return {"error": "Metadata API errors", "details": result["errors"]}

    published = result.get("data", {}).get("publishedDatasources")
    if not published:
        return {"error": "No publishedDatasources in response", "raw": result}

    fields = published[0].get("fields")
    if fields is None:
        return {"error": "No fields in publishedDatasources[0]", "raw": published[0]}

    return fields

# ────────────────────────────────────────────────────────────────────────────────
# Entrypoint
# ────────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("📊  VizQL MCP server starting…")
    mcp.run(transport="stdio")
