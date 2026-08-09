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

    video_list = []

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        links = soup.find_all("a", href=True)

        for a in links:
            href = a["href"]
            title = a.get_text(strip=True)

            img_tag = a.find("img")
            img_url = (
                img_tag["src"] if img_tag and "src" in img_tag.attrs else ""
            )

            res_match = re.search(r"(\d{3,4}p|HD|4K)", title, re.IGNORECASE)
            resolution = res_match.group(0) if res_match else "Unknown"

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

    except Exception as e:
        print(f"Error occurred during scraping: {e}")

    # ওয়েবসাইট রেসপন্স দিক বা না দিক, ফাইলটি তৈরি হবে
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(video_list, f, ensure_ascii=False, indent=4)

    print(f"Successfully saved {len(video_list)} items to data.json")


if __name__ == "__main__":
    scrape_hdvideo()
