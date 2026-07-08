"""GitHub API Integration Service"""
import httpx
import logging

logger = logging.getLogger(__name__)

class GitHubIntegrationService:
    @staticmethod
    async def process_pull_request(payload: dict):
        """GitHub'dan gelen PR webhook verisini işler."""
        action = payload.get("action")
        pr_data = payload.get("pull_request", {})
        repo_data = payload.get("repository", {})
        
        if action not in ["opened", "synchronize"]:
            return {"status": "ignored", "reason": f"Action '{action}' is not tracked."}
            
        repo_full_name = repo_data.get("full_name")
        pr_number = pr_data.get("number")
        clone_url = repo_data.get("clone_url")
        
        logger.info(f"PR #{pr_number} detected on {repo_full_name}. Action: {action}")
        
        # Burası ileride repodan kodları çekip analiz motoruna (Advanced Analysis & Fix Engine) 
        # paslayacağımız tetikleyici nokta olacak.
        return {
            "status": "success",
            "repo": repo_full_name,
            "pr_number": pr_number,
            "msg": "PR değişiklikleri analiz sırasına alındı."
        }

    @staticmethod
    async def post_comment_to_pr(repo_full_name: str, pr_number: int, comment: str, token: str):
        """Analiz sonuçlarını ve AI Fix önerilerini PR'a yorum olarak yazar."""
        url = f"https://api.github.com/repos/{repo_full_name}/issues/{pr_number}/comments"
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json={"body": comment}, headers={headers})
            if response.status_code == 201:
                return True
            logger.error(f"GitHub API Error: {response.text}")
            return False
