from mcp.server.fastmcp import FastMCP

from posthog_mcp.tools.annotations.annotations import create_annotation_request
from posthog_mcp.tools.docs.docs import search_docs
from posthog_mcp.tools.insights.insights import get_insight_details, get_insights
from posthog_mcp.tools.projects.projects import get_current_organization, list_projects
from posthog_mcp.tools.queries.queries import get_query, create_query

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
        
    return f"Available projects ({len(projects)}):\n" + "\n".join(
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

@mcp.tool()
async def list_posthog_insights(project_id: int, search: str | None = None) -> str:
    """List all available PostHog insights for a project.
    
    Args:
        project_id: The ID of the project as an integer (e.g. 99423)
        search: Optional search query to filter insights
    """
    try:
        insights = await get_insights(project_id, search)
        
        if not insights:
            return "No insights found"
            
        formatted_insights = []
        for i in insights:
            insight_id = i.get('id') or i.get('short_id', 'N/A')
            name = i.get('name') or i.get('derived_name', 'Unnamed')
            formatted_insights.append(f"ID: {insight_id} - Name: {name}")
            
        return f"Available insights ({len(insights)}):\n" + "\n".join(formatted_insights)
    except Exception as e:
        return f"Failed to list insights: {str(e)}"

@mcp.tool()
async def search_posthog_insights(project_id: int, search: str) -> str:
    """Search for PostHog insights by name.
    
    Args:
        project_id: The ID of the project as an integer (e.g. 99423)
        search: The search query to filter insights by name
    """
    try:
        insights = await get_insights(project_id, search)
        
        if not insights:
            return "No insights found"
            
        formatted_insights = []
        for i in insights:
            insight_id = i.get('id') or i.get('short_id', 'N/A')
            name = i.get('name') or i.get('derived_name', 'Unnamed')
            formatted_insights.append(f"ID: {insight_id} - Name: {name}")
            
        return f"Search results ({len(insights)}):\n" + "\n".join(formatted_insights)
    except Exception as e:
        return f"Failed to search insights: {str(e)}"

@mcp.tool()
async def get_posthog_insight_details(project_id: int, insight_id: int) -> str:
    """Get details for a specific PostHog insight.
    
    Args:
        project_id: The ID of the project as an integer (e.g. 99423)
        insight_id: The ID of the insight as an integer (e.g. 12345)
    """
    try:
        insight_details = await get_insight_details(project_id, insight_id)
        
        if not insight_details:
            return "No insight details found"
            
        formatted_details = []
        for key, value in insight_details.items():
            formatted_details.append(f"{key}: {value}")
            
        return "Insight details:\n" + "\n".join(formatted_details)
    except Exception as e:
        return f"Failed to get insight details: {str(e)}"

@mcp.tool()
async def get_posthog_query(project_id: str, query_id: str) -> str:
    """PostHog의 특정 쿼리 정보를 조회합니다.
    
    Args:
        project_id: PostHog 프로젝트 ID (예: "53497")
        query_id: 조회할 쿼리 ID
    """
    try:
        result = await get_query(project_id, query_id)
        
        if "error" in result:
            return f"쿼리 조회 실패: {result['error']}"
            
        return f"""쿼리 정보:
ID: {result.get('id', 'N/A')}
상태: {result.get('query_status', {}).get('status', 'N/A')}
완료 여부: {result.get('query_status', {}).get('complete', False)}
결과: {result.get('query_status', {}).get('results', 'N/A')}
"""
    except Exception as e:
        return f"쿼리 조회 중 오류 발생: {str(e)}"

@mcp.tool()
async def run_hogql_query(query: str) -> str:
    """PostHog에서 HogQL 쿼리를 실행합니다.
    
    Args:
        query: 실행할 HogQL 쿼리 문자열 (예: "select event from events limit 100")
    """
    try:
        # 현재 조직의 첫 번째 프로젝트를 가져옵니다
        org = await get_current_organization()
        if "error" in org:
            return f"조직 정보 조회 실패: {org['error']}"
        
        projects = await list_projects(org["id"])
        if "error" in projects:
            return f"프로젝트 목록 조회 실패: {projects['error']}"
        
        if not projects:
            return "사용 가능한 프로젝트가 없습니다."
        
        # 첫 번째 프로젝트를 사용
        project_id = str(projects[0]["id"])
        
        query_data = {
            "kind": "HogQLQuery",
            "query": query
        }
        
        result = await create_query(project_id, query_data)
        
        if "error" in result:
            return f"쿼리 실행 실패: {result['error']}"
            
        if "results" in result:
            return f"""쿼리 실행 결과:
{result['results']}"""
        else:
            return f"""쿼리 상태:
ID: {result.get('id', 'N/A')}
상태: {result.get('status', 'N/A')}
진행률: {result.get('progress', 0)}%
"""
    except Exception as e:
        return f"쿼리 실행 중 오류 발생: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport='stdio')
