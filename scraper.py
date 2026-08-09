import json
import re
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup


def scrape_hdvideo():
    base_url = "https://hdvideo9.com/"

    # ব্রাউজার সেশন তৈরি করা যাতে ব্লকিং এড়িয়ে যাওয়া যায়
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                " (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            ),
            "Accept": (
                "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
            ),
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://google.com",
        }
    )

    video_list = []

    try:
        response = session.get(base_url, timeout=20)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # সাইটের সকল লিঙ্ক সংগ্রহ করা
        links = soup.find_all("a", href=True)

        for a in links:
            href = a["href"]
            title = a.get_text(strip=True)

            # ছবি খোঁজা
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

            # রেজুলেশন বের করা
            res_match = re.search(
                r"(\d{3,4}p|1080p|720p|480p|360p|HD|4K)",
                f"{title} {href}",
                re.IGNORECASE,
            )
            resolution = res_match.group(0) if res_match else "Unknown"

            full_link = (
                href if href.startswith("http") else urljoin(base_url, href)
            )

            # যদি সরাসরি .mp4 লিঙ্ক হয়
            is_mp4 = full_link.lower().endswith(".mp4")

            # ফাঁকা শিরোনাম এড়িয়ে চলা
            if title and len(title) > 2 and full_link != base_url:
                video_list.append(
                    {
                        "title": title,
                        "link": full_link,
                        "image": img_url,
                        "resolution": resolution,
                        "is_direct_mp4": is_mp4,
                    }
                )

        # ডুপ্লিকেট লিঙ্ক ফিল্টার করা
        seen = set()
        unique_videos = []
        for item in video_list:
            if item["link"] not in seen:
                seen.add(item["link"])
                unique_videos.append(item)

        video_list = unique_videos

    except Exception as e:
        print(f"Error fetching data: {e}")

    # ফাইল সেভ করা (কোনো ডেটা না পেলেও অন্তত এরর ট্র্যাকিং ডাটা থাকবে)
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(video_list, f, ensure_ascii=False, indent=4)

    print(f"Scraped and saved {len(video_list)} items to data.json")


if __name__ == "__main__":
    scrape_hdvideo()
