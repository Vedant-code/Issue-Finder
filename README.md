# Algo-Issue-Finder

![Algo-Issue-Finder Banner](assets/banner.jpg)

A lightweight Python utility that crawls the GitHub Search API to find open, unassigned, beginner-friendly issues (`good first issue`) matching specific technical and algorithmic topics. 

Standard GitHub search makes it easy to filter by labels or languages, but makes it hard to target deep, specific concepts (like graphs, optimization, dynamic programming, or data structures) across the platform. This tool solves that by automating complex topic-focused queries and compiling the results into a clean markdown report.

## Features

- **Topic-Focused Search:** Targets specific algorithmic concepts (e.g., Graphs, Time Complexity, DP, Data Structures) instead of generic tags.
- **Noise Filtering:** Uses filters like `no:assignee`, `is:issue`, and `is:open` to ensure you only see actionable issues.
- **Rate-Limit Resilience:** Automatically respects the GitHub API rate limits by reading the reset headers and pausing requests dynamically.
- **Structured Markdown Reports:** Outputs a categorized [results.md](results.md) report containing direct links to the relevant repositories and issues.

## Installation

This project requires Python 3.11+ and uses `requests`.

If you have `uv` installed:
```bash
uv sync
```

Otherwise, install the dependencies using `pip`:
```bash
pip install -r requirements.txt
# or simply
pip install requests
```

## Configuration

The script uses a GitHub Personal Access Token (PAT) to increase API rate limits. 

1. Create a Personal Access Token (classic or fine-grained) on GitHub with read-only permissions for public repositories.
2. Set the token as an environment variable:

**On Windows (PowerShell):**
```powershell
$env:GITHUB_TOKEN="your_github_token_here"
```

**On Linux/macOS:**
```bash
export GITHUB_TOKEN="your_github_token_here"
```

*Note: The script will still run without a token, but you will be heavily rate-limited by GitHub's public search API.*

## Usage

Run the crawler:
```bash
python main.py
```

The script will fetch matches for your queries and save them directly to [results.md](results.md).

## Customizing Search Topics

You can easily customize the search to target the exact technologies, concepts, or languages you want to practice. Open [main.py](main.py) and modify the `queries` and `query_labels` lists:

```python
queries = [
    # Search for graph traversal issues in Python
    'is:issue is:open no:assignee label:"good first issue" "graph" OR "knowledge graph" language:python',
    # Search for performance bottlenecks
    'is:issue is:open no:assignee label:"good first issue" "time complexity" OR "O(n)" language:python',
]

query_labels = [
    'Graph-based / Knowledge Graphs (`good first issue`)',
    'Time Complexity & Big-O (`good first issue`)',
]
```
