from typing import Any, Dict, Optional

from posthog_mcp.core import settings
from posthog_mcp.core.client import PostHogClient

client = PostHogClient()

async def create_query(
    project_id: str,
    query: Dict[str, Any],
    refresh: str = "blocking"
) -> Dict[str, Any]:
    """PostHog에 새로운 쿼리를 생성하고 실행합니다.
    
    Args:
        project_id: PostHog 프로젝트 ID
        query: 실행할 쿼리 정보 (예: {"kind": "HogQLQuery", "query": "select * from events limit 100"})
        refresh: 쿼리 실행 방식 ('blocking', 'async', 'force_blocking' 등)
        
    Returns:
        Dict[str, Any]: 쿼리 실행 결과
    """
    endpoint = f"/api/projects/{project_id}/query/"
    data = {
        "query": query,
        "refresh": refresh
    }
    return await client.post(endpoint, data=data)

async def get_query(project_id: str, query_id: str) -> Dict[str, Any]:
    """PostHog의 특정 쿼리 정보를 조회합니다.
    
    Args:
        project_id: PostHog 프로젝트 ID
        query_id: 조회할 쿼리 ID
        
    Returns:
        Dict[str, Any]: 쿼리 상태 및 결과 정보
    """
    endpoint = f"/api/projects/{project_id}/query/{query_id}"
    return await client.get(endpoint) 