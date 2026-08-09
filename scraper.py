import json
import re
import requests
from bs4 import BeautifulSoup


def scrape_hdvideo():
    url = "https://hdvideo9.com/"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            " (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching website: {e}")
        return

    soup = BeautifulSoup(response.text, "html.parser")
    video_list = []

    # ওয়েবসাইটের স্ট্রাকচার অনুযায়ী সব ভিডিও লিঙ্ক বা আইটেম ব্লক খুঁজে বের করা
    # সাধারণত <a> ট্যাগের মধ্যে লিঙ্ক থাকে
    links = soup.find_all("a", href=True)

    for a in links:
        href = a["href"]

        # যদি কোনো নির্দিষ্ট ভিডিও পেজ বা পেজ লিঙ্ক হয়
        title = a.get_text(strip=True)

        # ইমেজ খোঁজা (লিঙ্কের ভেতর বা কাছাকাছি)
        img_tag = a.find("img")
        img_url = img_tag["src"] if img_tag and "src" in img_tag.attrs else ""

        # রেজুলেশন ম্যাচ করা (যেমন: 720p, 1080p, HD ইত্যাদি)
        res_match = re.search(r"(\d{3,4}p|HD|4K)", title, re.IGNORECASE)
        resolution = res_match.group(0) if res_match else "Unknown"

        # MP4 লিঙ্ক সরাসরি থাকলে বা ডিরেক্ট ভিডিও লিঙ্ক
        is_mp4 = href.endswith(".mp4")

        if title and href:
            video_list.append(
                {
                    "title": title,
                    "page_url": href,
                    "image": img_url,
                    "resolution": resolution,
                    "is_direct_mp4": is_mp4,
                }
            )

    # স্ক্র্যাপ করা ডেটা JSON ফাইলে সেভ করা
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(video_list, f, ensure_ascii=False, indent=4)

    print(f"Successfully scraped {len(video_list)} items.")


if __name__ == "__main__":
    scrape_hdvideo()
