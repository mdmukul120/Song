import json
import re
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import cloudscraper


def scrape_category():
    target_url = (
        "https://hdvideo9.com/category/bollywood-movie-video-songs.html"
    )
    base_url = "https://hdvideo9.com/"

    # Cloudflare Anti-Bot Bypass Client
    scraper = cloudscraper.create_scraper(
        browser={"browser": "chrome", "platform": "windows", "desktop": True}
    )

    video_list = []

    try:
        print(f"Fetching category page: {target_url}")
        response = scraper.get(target_url, timeout=25)

        if response.status_code != 200:
            print(f"Failed to fetch page. Status code: {response.status_code}")
            return

        soup = BeautifulSoup(response.text, "html.parser")

        # HTML ডকুমেন্টের সকল 'a' ট্যাগ অ্যানালিসিস করা
        links = soup.find_all("a", href=True)

        for a in links:
            href = a["href"].strip()
            title = a.get_text(strip=True)

            # হোমপেজ, ক্যাটাগরি লিঙ্ক বা অপ্রয়োজনীয় নেভিগেশন ফিল্টার করা
            if not href or href == "#" or href == base_url or "javascript:" in href:
                continue

            full_link = (
                href if href.startswith("http") else urljoin(base_url, href)
            )

            # ইমেজ খোঁজা
            img_tag = a.find("img") or (
                a.parent.find("img") if a.parent else None
            )
            img_url = ""
            if img_tag:
                img_url = (
                    img_tag.get("src")
                    or img_tag.get("data-src")
                    or img_tag.get("data-lazy-src")
                    or ""
                )
                if img_url and not img_url.startswith("http"):
                    img_url = urljoin(base_url, img_url)

            # রেজুলেশন অ্যানালিসিস
            res_match = re.search(
                r"(\d{3,4}p|1080p|720p|480p|360p|HD|4K)",
                f"{title} {href}",
                re.IGNORECASE,
            )
            resolution = res_match.group(0) if res_match else "Unknown"

            is_mp4 = full_link.lower().endswith(".mp4")

            # উপযুক্ত ডেটা থাকলে লিস্টে যোগ
            if title and len(title) > 2:
                video_list.append(
                    {
                        "title": title,
                        "link": full_link,
                        "image": img_url,
                        "resolution": resolution,
                        "is_direct_mp4": is_mp4,
                    }
                )

        # Duplicate Clean Up
        seen = set()
        unique_videos = []
        for item in video_list:
            if item["link"] not in seen:
                seen.add(item["link"])
                unique_videos.append(item)

        video_list = unique_videos

    except Exception as e:
        print(f"Scraping Error: {e}")

    # ডেটা জেসন ফাইলে সেভ করা
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(video_list, f, ensure_ascii=False, indent=4)

    print(f"Successfully scraped {len(video_list)} links into data.json")


if __name__ == "__main__":
    scrape_category()
