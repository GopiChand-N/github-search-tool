import requests
from dotenv import load_dotenv
import os
import base64
from rich import print
from rich.panel import Panel
from rich.text import Text
from rich.console import Console
from rich.rule import Rule

# Initialize Rich console
console = Console()

# Load environment variables
load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# Base GitHub API URL
GITHUB_API_URL = "https://api.github.com/search/repositories"

def get_headers():
    headers = {"Accept": "application/vnd.github.v3+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    return headers

def get_top_contributors(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/contributors"
    response = requests.get(url, headers=get_headers())
    if response.status_code == 200:
        contributors = response.json()
        return [c['login'] for c in contributors[:3]]
    return []

def get_readme_snippet(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/readme"
    response = requests.get(url, headers=get_headers())
    if response.status_code == 200:
        content = response.json().get("content", "")
        decoded = base64.b64decode(content).decode(errors='ignore')
        return decoded[:300] + "..." if len(decoded) > 300 else decoded
    return "README not available."

def search_github_repositories(query, language=None, license=None, sort="stars", max_results=5):
    if language:
        query += f" language:{language}"
    if license:
        query += f" license:{license}"

    params = {
        "q": query,
        "sort": sort,
        "order": "desc",
        "per_page": max_results
    }

    console.print(f"\n🔍 [bold green]Searching GitHub for[/bold green]: '{query}' | Sorted by: [bold cyan]{sort}[/bold cyan]\n")

    response = requests.get(GITHUB_API_URL, params=params, headers=get_headers())

    if response.status_code == 200:
        repositories = response.json()['items']
        for i, repo in enumerate(repositories, 1):
            contributors = get_top_contributors(repo['owner']['login'], repo['name'])
            readme_snippet = get_readme_snippet(repo['owner']['login'], repo['name'])

            text = Text()
            text.append(f"{i}. {repo['full_name']}\n", style="bold yellow")
            text.append(f"   🌟 Stars: {repo['stargazers_count']}   🍴 Forks: {repo['forks_count']}   🐛 Open Issues: {repo['open_issues_count']}\n", style="cyan")
            text.append(f"   📜 License: {repo['license']['name'] if repo['license'] else 'None'}   ⏰ Updated: {repo['updated_at']}\n", style="dim")
            text.append(f"   👤 Owner: {repo['owner']['login']}   🔗 URL: {repo['html_url']}\n", style="blue")
            text.append(f"\n   📄 Description: {repo['description'] or 'No description provided.'}\n", style="italic")
            text.append(f"   👥 Top Contributors: {', '.join(contributors) if contributors else 'Not available'}\n", style="magenta")
            text.append(f"   📘 README Snippet:\n   {readme_snippet}\n", style="white")

            console.print(Panel(text, border_style="bright_blue", expand=False))
            console.print(Rule())

    else:
        console.print(f"[bold red]❌ Error: {response.status_code} - {response.text}[/bold red]")

# Main program
if __name__ == "__main__":
    query = input("Enter your GitHub search query: ").strip()
    language = input("Filter by programming language (optional): ").strip() or None
    license_type = input("Filter by license (e.g., mit, gpl-3.0) (optional): ").strip() or None
    sort_by = input("Sort by 'stars' or 'updated' (default is stars): ").strip().lower() or "stars"
    max_results = input("How many results do you want to see? (default 5): ").strip()
    max_results = int(max_results) if max_results else 5

    search_github_repositories(query, language, license_type, sort_by, max_results)
