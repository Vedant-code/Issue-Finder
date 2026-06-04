import os
import requests
import time
from datetime import datetime

OUTPUT_FILE = "results.md"
RESULTS_PER_PAGE = 10
MAX_PAGES = 10  # GitHub Search API caps at 1000 results (100 pages x 10)

def wait_for_rate_limit(response):
    reset_ts = response.headers.get("X-RateLimit-Reset")
    if reset_ts:
        wait = max(0, int(reset_ts) - int(time.time())) + 2
    else:
        wait = 60
    print(f"Rate limit hit. Waiting {wait} seconds before retrying...")
    time.sleep(wait)

def fetch_page(api_url, headers, params, retries=5):
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(api_url, headers=headers, params=params)
            if response.status_code == 200:
                return response
            elif response.status_code == 403:
                wait_for_rate_limit(response)
            elif response.status_code == 422:
                print(f"Query rejected by GitHub (422): {response.json().get('message', '')}")
                return None
            else:
                print(f"Error {response.status_code}: {response.text}")
                return None
        except Exception as e:
            print(f"Request error (attempt {attempt}/{retries}): {e}")
            time.sleep(10)
    print("Max retries reached. Moving on.")
    return None

def crawl_github_algorithm_issues():
    API_URL = "https://api.github.com/search/issues"

    GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

    headers = {"Accept": "application/vnd.github.v3+json"}
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
    print(f"Results will be saved to: {OUTPUT_FILE}\n")

    md_lines = [
        "# GitHub Algorithm & Architecture Issues",
        f"\n_Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_\n",
    ]

    total_collected = 0

    for i, (query, label) in enumerate(zip(queries, query_labels), 1):
        print(f"\n=== Query {i}/{len(queries)}: {label} ===")
        md_lines.append(f"\n## Query {i}: {label}\n")

        query_count = 0
        seen_ids = set()

        for page in range(1, MAX_PAGES + 1):
            print(f"  Fetching page {page}...")

            params = {
                "q": query,
                "sort": "updated",
                "order": "desc",
                "per_page": RESULTS_PER_PAGE,
                "page": page,
            }

            response = fetch_page(API_URL, headers, params)
            if response is None:
                break

            data = response.json()
            total_count = data.get("total_count", 0)
            issues = data.get("items", [])

            if not issues:
                print(f"  No more results on page {page}.")
                break

            new_issues = 0
            for issue in issues:
                if issue["id"] in seen_ids or "pull_request" in issue:
                    continue
                seen_ids.add(issue["id"])

                repo_url = issue["repository_url"].replace(
                    "api.github.com/repos/", "github.com/"
                )
                print(f"  Title: {issue['title']}")
                print(f"  Repo:  {repo_url}")
                print(f"  Link:  {issue['html_url']}")
                print(f"  {'-' * 46}")

                md_lines.append(f"### {issue['title']}")
                md_lines.append(f"- **Repo:** [{repo_url}]({repo_url})")
                md_lines.append(f"- **Issue:** [{issue['html_url']}]({issue['html_url']})\n")

                new_issues += 1
                query_count += 1
                total_collected += 1

            # Save after every page so progress isn't lost
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                f.write("\n".join(md_lines))

            print(f"  Page {page}: {new_issues} new issues (query total: {query_count} / {total_count} available)")

            if page * RESULTS_PER_PAGE >= min(total_count, MAX_PAGES * RESULTS_PER_PAGE):
                print(f"  All available results collected for this query.")
                break

            # Polite delay between pages
            time.sleep(6)

        print(f"  Query {i} done — {query_count} issues collected.")

        # Delay between queries
        if i < len(queries):
            print(f"\nSleeping 6 seconds before next query...\n")
            time.sleep(6)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    print(f"\nDone! {total_collected} issues collected in total.")
    print(f"Results saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    crawl_github_algorithm_issues()
