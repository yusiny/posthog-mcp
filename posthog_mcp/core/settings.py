import os
from typing import Literal

from dotenv import load_dotenv

load_dotenv()

REGION_ENDPOINTS = {
    "us": "https://us.posthog.com",
    "eu": "https://eu.posthog.com"
}

PERSONAL_API_KEY = os.getenv("PERSONAL_API_KEY")
POSTHOG_REGION: Literal["us", "eu"] = os.getenv("POSTHOG_REGION", "us")
API_ENDPOINT = REGION_ENDPOINTS[POSTHOG_REGION]

# API Endpoints
CURRENT_ORG_ENDPOINT = "/api/organizations/@current/"
PROJECTS_ENDPOINT = "/api/organizations/{org_id}/projects/"
ANNOTATIONS_ENDPOINT = "/api/projects/{project_id}/annotations/" 