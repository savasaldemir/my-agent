"""GitHub Webhook Web Alıcısı Router"""
from fastapi import APIRouter, Request, Header, HTTPException, status
from ..services.github_service import GitHubIntegrationService

router = APIRouter(
    prefix="/webhooks/github",
    tags=["github-integration"]
)

@router.post("", status_code=status.HTTP_202_ACCEPTED)
async def github_webhook_receiver(request: Request, x_github_event: str = Header(None)):
    """GitHub Webhook'larından gelen anlık push ve PR olaylarını yakalar."""
    if not x_github_event:
        raise HTTPException(status_code=400, detail="Eksik X-GitHub-Event header bilgisi.")
        
    payload = await request.json()
    
    if x_github_event == "ping":
        return {"msg": "GitHub Webhook bağlantısı aktif ve başarılı!"}
        
    if x_github_event == "pull_request":
        result = await GitHubIntegrationService.process_pull_request(payload)
        return result
        
    return {"status": "unsupported_event", "event": x_github_event}
