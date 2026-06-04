import os
import requests
import time
from datetime import datetime

OUTPUT_FILE = "results.md"

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

    query_labels = [
        'Python — `O(n^2)` / `time complexity` + `performance`',
        'C++ — `memory leak` / `bottleneck` + `performance`',
        'Python — `algorithm` + `help wanted`',
        'C++ — `bottleneck` + `help wanted`',
    ]

    print("Starting GitHub API Crawler for Algorithm/Architecture Issues...\n")

    md_lines = [
        "# GitHub Algorithm & Architecture Issues",
        f"\n_Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_\n",
    ]

    for i, (query, label) in enumerate(zip(queries, query_labels), 1):
        print(f"--- Query {i}: {query} ---")

        md_lines.append(f"\n## Query {i}: {label}\n")

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
                    msg = "No open issues found for this query right now."
                    print(msg + "\n")
                    md_lines.append(f"_{msg}_\n")
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

                            md_lines.append(f"### {issue['title']}")
                            md_lines.append(f"- **Repo:** [{repo_url}]({repo_url})")
                            md_lines.append(f"- **Issue:** [{issue['html_url']}]({issue['html_url']})\n")

            elif response.status_code == 403:
                msg = "Rate limit hit. Consider adding a GitHub Personal Access Token."
                print(msg)
                md_lines.append(f"> {msg}\n")
                break
            else:
                msg = f"Error {response.status_code}: {response.text}"
                print(msg)
                md_lines.append(f"> {msg}\n")

        except Exception as e:
            msg = f"An error occurred: {e}"
            print(msg)
            md_lines.append(f"> {msg}\n")

        print()
        if i < len(queries):
            print("Sleeping 6 seconds to respect rate limits...\n")
            time.sleep(6)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    print(f"\nResults saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    crawl_github_algorithm_issues()
