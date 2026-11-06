import requests
import re

USERNAME = "guigarciamonteiro"
GRAPHQL_URL = "https://leetcode.com/graphql"

QUERY = """
query getUserProfile($username: String!) {
  matchedUser(username: $username) {
    username
    submitStats: submitStatsGlobal {
      acSubmissionNum {
        difficulty
        count
      }
    }
    recentSubmissionList(limit: 5) {
      title
      titleSlug
      statusDisplay
      lang
    }
  }
}
"""

def fetch_leetcode_data():
    response = requests.post(
        GRAPHQL_URL,
        json={"query": QUERY, "variables": {"username": USERNAME}},
        headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
    )
    if response.status_code == 200:
        return response.json()["data"]["matchedUser"]
    else:
        raise Exception(f"Erro na API do LeetCode: {response.status_code}")

def generate_markdown(data):
    stats = {item['difficulty']: item['count'] for item in data['submitStats']['acSubmissionNum']}
    recent = data['recentSubmissionList']

    md = f"### 🧩 LeetCode Stats\n\n"
    md += f"- **Total Resolvido:** {stats.get('All', 0)} (🟢 Easy: {stats.get('Easy', 0)} | 🟡 Medium: {stats.get('Medium', 0)} | 🔴 Hard: {stats.get('Hard', 0)})\n\n"
    md += "#### 🕒 Últimas Submissões\n\n"
    
    for sub in recent:
        if sub['statusDisplay'] == 'Accepted':
            url = f"https://leetcode.com/problems/{sub['titleSlug']}/"
            md += f"- [{sub['title']}]({url}) — `{sub['lang']}` ✅\n"
            
    return md

def update_readme(new_content):
    with open("README.md", "r", encoding="utf-8") as f:
        readme = f.read()

    pattern = r"(<!-- LEETCODE:START -->)(.*?)(<!-- LEETCODE:END -->)"
    replacement = f"\\1\n{new_content}\n\\3"
    
    updated_readme = re.sub(pattern, replacement, readme, flags=re.DOTALL)

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(updated_readme)

if __name__ == "__main__":
    data = fetch_leetcode_data()
    md_content = generate_markdown(data)
    update_readme(md_content)