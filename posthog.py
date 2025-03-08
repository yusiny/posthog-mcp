import os
from datetime import datetime, timezone
from typing import Any, List

import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

API_ENDPOINT = "https://us.posthog.com"
PERSONAL_API_KEY = os.getenv("PERSONAL_API_KEY")

# Initialize FastMCP server
mcp = FastMCP("posthog")

async def get_current_organization() -> dict[str, Any]:
    """Get current organization details."""
    if not PERSONAL_API_KEY:
        return {"error": "PERSONAL_API_KEY environment variable is not set"}
        
    headers = {"Authorization": f"Bearer {PERSONAL_API_KEY}"}
    url = f"{API_ENDPOINT}/api/organizations/@current/"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}

async def list_projects(org_id: str) -> List[dict[str, Any]]:
    """List all projects in an organization."""
    if not PERSONAL_API_KEY:
        return {"error": "PERSONAL_API_KEY environment variable is not set"}
        
    headers = {"Authorization": f"Bearer {PERSONAL_API_KEY}"}
    url = f"{API_ENDPOINT}/api/organizations/{org_id}/projects/"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])
        except Exception as e:
            return {"error": str(e)}

async def create_annotation(project_id: int, content: str, date_marker: str | None = None) -> dict[str, Any]:
    """Make a request to create a PostHog annotation."""
    if not PERSONAL_API_KEY:
        return {"error": "PERSONAL_API_KEY environment variable is not set"}
        
    headers = {
        "Authorization": f"Bearer {PERSONAL_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "content": content,
        "date_marker": date_marker or datetime.now(timezone.utc).isoformat()
    }

    url = f"{API_ENDPOINT}/api/projects/{str(project_id)}/annotations/"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=data, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}

@mcp.tool()
async def list_posthog_projects() -> str:
    """List all available PostHog projects."""
    org = await get_current_organization()
    if "error" in org:
        return f"Failed to get organization: {org['error']}"
    
    projects = await list_projects(org["id"])
    if "error" in projects:
        return f"Failed to list projects: {projects['error']}"
    
    if not projects:
        return "No projects found"
        
    return "Available projects:\n" + "\n".join(
        f"ID: {p['id']} - Name: {p['name']}" for p in projects
    )

@mcp.tool()
async def create_posthog_annotation(project_id: int, content: str, date_marker: str | None = None) -> str:
    """Create a PostHog annotation.
    
    Args:
        project_id: The ID of the project as an integer (e.g. 99423)
        content: The content/text of the annotation
        date_marker: Optional ISO-8601 timestamp for the annotation (e.g. 2024-03-20T14:15:22Z)
    """
    result = await create_annotation(project_id, content, date_marker)
    
    if "error" in result:
        return f"Failed to create annotation: {result['error']}"
        
    return f"""Successfully created annotation:
ID: {result['id']}
Content: {result['content']}
Date: {result.get('date_marker', 'Now')}
Created by: {result['created_by']['email']}
"""

if __name__ == "__main__":
    mcp.run(transport='stdio')


