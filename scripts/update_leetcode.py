"""Busca estatísticas públicas do LeetCode e gera leetcode.svg a partir do template."""
import os
import sys
from datetime import datetime, timezone
from xml.sax.saxutils import escape

import requests

USERNAME = "guigarciamonteiro"
GRAPHQL_URL = "https://leetcode.com/graphql"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(ROOT, "Assets", "leetcode_template.svg")
OUTPUT = os.path.join(ROOT, "Assets", "leetcode.svg")
MAX_RECENT = 3

QUERY = """
query getUserProfile($username: String!, $limit: Int!) {
  matchedUser(username: $username) {
    username
    submitStats: submitStatsGlobal {
      acSubmissionNum {
        difficulty
        count
      }
    }
  }
  recentSubmissionList(username: $username, limit: $limit) {
    title
    titleSlug
    statusDisplay
    lang
  }
}
"""


def fetch_leetcode_data() -> dict:
    response = requests.post(
        GRAPHQL_URL,
        json={"query": QUERY, "variables": {"username": USERNAME, "limit": 20}},
        headers={
            "Content-Type": "application/json",
            "Referer": "https://leetcode.com",
            "User-Agent": "Mozilla/5.0",
        },
        timeout=30,
    )
    if response.status_code != 200:
        raise Exception(f"Erro na API do LeetCode: {response.status_code}")

    payload = response.json()
    if payload.get("errors"):
        raise Exception(f"Erro GraphQL: {payload['errors']}")
    data = payload.get("data") or {}
    if not data.get("matchedUser"):
        raise Exception(f"Usuário '{USERNAME}' não encontrado.")
    return data


def truncate(text: str, size: int) -> str:
    return text if len(text) <= size else text[: size - 1] + "…"


def build_values(data: dict) -> dict:
    user = data["matchedUser"]
    stats = {i["difficulty"]: i["count"] for i in user["submitStats"]["acSubmissionNum"]}

    # Últimas submissões aceitas, sem repetir problema
    recent, seen = [], set()
    for sub in data.get("recentSubmissionList") or []:
        if sub["statusDisplay"] != "Accepted" or sub["titleSlug"] in seen:
            continue
        seen.add(sub["titleSlug"])
        recent.append(f'> {truncate(sub["title"], 48)}  [{sub["lang"]}]')
        if len(recent) == MAX_RECENT:
            break
    recent += [""] * (MAX_RECENT - len(recent))

    values = {
        "USERNAME": "GARC1A04",
        "SOLVED": str(stats.get("All", 0)),
        "EASY": str(stats.get("Easy", 0)),
        "MEDIUM": str(stats.get("Medium", 0)),
        "HARD": str(stats.get("Hard", 0)),
        "UPDATED": datetime.now(timezone.utc).strftime("%d/%m/%Y").upper(),
    }
    for i, line in enumerate(recent, start=1):
        values[f"RECENT{i}"] = line
    return values


def render(values: dict) -> None:
    with open(TEMPLATE, "r", encoding="utf-8") as f:
        svg = f.read()
    for key, val in values.items():
        svg = svg.replace("{{" + key + "}}", escape(val))  # escapa &, <, > dos títulos
    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(svg)


if __name__ == "__main__":
    try:
        values = build_values(fetch_leetcode_data())
    except Exception as e:
        print(f"Erro: {e}", file=sys.stderr)
        sys.exit(1)
    render(values)
    print(f"{OUTPUT} atualizado: {values}")