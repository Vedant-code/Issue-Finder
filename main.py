import os
import requests
import time

def crawl_github_algorithm_issues():
    API_URL = "https://api.github.com/search/issues"

    GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

    headers = {
        "Accept": "application/vnd.github.v3+json"
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"

    queries = [
        'is:issue is:open no:assignee "O(n^2)" OR "time complexity" label:performance language:python',
        'is:issue is:open no:assignee "memory leak" OR "bottleneck" label:performance language:cpp',
        'is:issue is:open no:assignee label:algorithm label:"help wanted" language:python',
        'is:issue is:open no:assignee "bottleneck" label:"help wanted" language:cpp',
    ]

    print("Starting GitHub API Crawler for Algorithm/Architecture Issues...\n")

    for i, query in enumerate(queries, 1):
        print(f"--- Query {i}: {query} ---")

        params = {
            "q": query,
            "sort": "updated",
            "order": "desc",
            "per_page": 5,
        }

        try:
            response = requests.get(API_URL, headers=headers, params=params)

            if response.status_code == 200:
                data = response.json()
                issues = data.get("items", [])

                if not issues:
                    print("No open issues found for this query right now.\n")
                else:
                    for issue in issues:
                        if "pull_request" not in issue:
                            repo_url = issue["repository_url"].replace(
                                "api.github.com/repos/", "github.com/"
                            )
                            print(f"Title: {issue['title']}")
                            print(f"Repo:  {repo_url}")
                            print(f"Link:  {issue['html_url']}")
                            print("-" * 50)

            elif response.status_code == 403:
                print("Rate limit hit. Consider adding a GitHub Personal Access Token.")
                break
            else:
                print(f"Error {response.status_code}: {response.text}")

        except Exception as e:
            print(f"An error occurred: {e}")

        print()
        if i < len(queries):
            print("Sleeping 6 seconds to respect rate limits...\n")
            time.sleep(6)


if __name__ == "__main__":
    crawl_github_algorithm_issues()
