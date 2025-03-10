from mcp.server.fastmcp import FastMCP

from posthog_mcp.tools.annotations.annotations import create_annotation_request
from posthog_mcp.tools.projects.projects import get_current_organization, list_projects

# Initialize FastMCP server
mcp = FastMCP("posthog")

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
    result = await create_annotation_request(project_id, content, date_marker)
    
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
