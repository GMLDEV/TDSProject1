import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "https://discourse.onlinedegree.iitm.ac.in"
CATEGORY_SLUG = "courses/tds-kb"
START_DATE = datetime(2025, 1, 1)
END_DATE = datetime(2025, 4, 15)
OUTPUT_FILE = "scraped_posts.json"

def get_csrf_token(session):
    """Get CSRF token via Discourse's API endpoint"""
    response = session.get(f"{BASE_URL}/session/csrf.json")
    if response.status_code != 200:
        raise Exception(f"CSRF fetch failed: {response.status_code}")
    return response.json()['csrf']

def login(session, username, password):
    """Authenticate using API-based CSRF token"""
    csrf_token = get_csrf_token(session)
    
    login_data = {
        "login": username,
        "password": password,
        "authenticity_token": csrf_token
    }
    
    response = session.post(
        f"{BASE_URL}/session",
        json=login_data,
        headers={"X-CSRF-Token": csrf_token}
    )
    
    if response.status_code != 200:
        raise Exception(f"Login failed: {response.json()['error']}")

def scrape_category(session):
    """Scrape posts with proper API headers"""
    # Get category ID from slug
    response = session.get(f"{BASE_URL}/c/{CATEGORY_SLUG}/posts.json")
    return response.json()['topic_list']['topics']

def main():
    with requests.Session() as session:
        # Set realistic headers
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Accept": "application/json",
            "Content-Type": "application/json"
        })

        # Get credentials (if needed)
        username = input("Enter IITM username: ")
        password = input("Enter IITM password: ")

        # Authenticate
        login(session, username, password)
        print("Login successful!")

        # Scrape and filter posts
        all_posts = []
        page = 0

        while True:
            print(f"Scraping page {page}...")
            response = session.get(
                f"{BASE_URL}/c/{CATEGORY_SLUG}.json",
                params={"page": page}
            )

            data = response.json()
            topics = data.get('topic_list', {}).get('topics', [])
            if not topics:
                break

            for topic in topics:
                post_date = datetime.strptime(topic['created_at'], "%Y-%m-%dT%H:%M:%S.%fZ")

                if post_date > END_DATE:
                    continue
                if post_date < START_DATE:
                    break

                # Fetch full topic content
                topic_id = topic['id']
                topic_details_resp = session.get(f"{BASE_URL}/t/{topic_id}.json")
                if topic_details_resp.status_code != 200:
                    print(f"Failed to get topic {topic_id}")
                    continue

                topic_details = topic_details_resp.json()
                first_post = topic_details['post_stream']['posts'][0]

                post_info = {
                    "id": topic_id,
                    "title": topic['title'],
                    "created_at": topic['created_at'],
                    "url": f"{BASE_URL}/t/{topic_id}",
                    "body": first_post.get('cooked', '')
                }

                all_posts.append(post_info)

            page += 1

        # Save results
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(all_posts, f, indent=2, ensure_ascii=False)

        print(f"Saved {len(all_posts)} posts to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()

