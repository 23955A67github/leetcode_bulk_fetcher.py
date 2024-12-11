import requests
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

# GraphQL query to fetch user profile data
QUERY = """
query userProfile($username: String!) {
  matchedUser(username: $username) {
    username
    profile {
      ranking
      userAvatar
      aboutMe
    }
    submitStats {
      acSubmissionNum {
        difficulty
        count
      }
    }
  }
}
"""

# Fetch data for a single user
def fetch_user_data(username):
    url = "https://leetcode.com/graphql/"
    headers = {"Content-Type": "application/json"}
    payload = {"query": QUERY, "variables": {"username": username}}
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to fetch data for {username}: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching data for {username}: {e}")
        return None

# Parse data from API response
def parse_data(json_data):
    user_data = json_data.get("data", {}).get("matchedUser", {})
    if not user_data:
        return None
    return {
        "username": user_data.get("username"),
        "ranking": user_data.get("profile", {}).get("ranking"),
        "avatar": user_data.get("profile", {}).get("userAvatar"),
        "about_me": user_data.get("profile", {}).get("aboutMe"),
        "total_problems_solved": sum(
            stat["count"] for stat in user_data.get("submitStats", {}).get("acSubmissionNum", [])
        ),
    }

# Main function to fetch data for all users
def fetch_all_user_data(usernames, output_file="leetcode_profiles.csv"):
    all_data = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(fetch_user_data, usernames))

    for raw_data in results:
        if raw_data:
            parsed_data = parse_data(raw_data)
            if parsed_data:
                all_data.append(parsed_data)

    # Save data to CSV
    df = pd.DataFrame(all_data)
    df.to_csv(output_file, index=False)
    print(f"Data saved to {output_file}")

if __name__ == "__main__":
    # Input: List of usernames
    usernames = ["user1", "user2", "user3"]  # Replace with actual LeetCode usernames

    # Output file name
    output_file = "leetcode_profiles.csv"

    # Fetch and save data
    fetch_all_user_data(usernames, output_file)
