import json
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import cloudscraper


def get_download_link_from_details(scraper, page_url, base_url):
    """ভিডিও ডিটেইলস পেজে ঢুকে আসল ডাউনলোড লিংক বের করার ফাংশন"""
    try:
        res = scraper.get(page_url, timeout=15)
        if res.status_code != 200:
            return None

        soup = BeautifulSoup(res.text, "html.parser")

        # ১. সরাসরি .mp4 বা .mkv এক্সটেনশনযুক্ত লিঙ্ক খোঁজা
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            if href.lower().endswith(
                (".mp4", ".mkv", ".avi", ".3gp")
            ) or "download" in href.lower():
                return (
                    href
                    if href.startswith("http")
                    else urljoin(base_url, href)
                )

        # ২. ডাউনলোড বোতাম বা নির্দিষ্ট ক্লাস/আইডি চেক করা
        download_btn = soup.find("a", string=lambda s: s and "Download" in s)
        if download_btn and download_btn.get("href"):
            href = download_btn["href"].strip()
            return href if href.startswith("http") else urljoin(base_url, href)

    except Exception as e:
        print(f"Error fetching details page {page_url}: {e}")

    return None


def scrape_category():
    target_url = (
        "https://hdvideo9.com/category/bollywood-movie-video-songs.html"
    )
    base_url = "https://hdvideo9.com/"

    # Cloudflare Bypass Scraper
    scraper = cloudscraper.create_scraper(
        browser={"browser": "chrome", "platform": "windows", "desktop": True}
    )

    final_data = []

    try:
        print(f"Fetching category page: {target_url}")
        response = scraper.get(target_url, timeout=25)

        if response.status_code != 200:
            print(f"Failed to fetch page. Status code: {response.status_code}")
            return

        soup = BeautifulSoup(response.text, "html.parser")
        links = soup.find_all("a", href=True)

        visited_urls = set()

        for a in links:
            href = a["href"].strip()

            # অপ্রয়োজনীয় নেভিগেশন ও হোমপেজের লিঙ্ক বাদ দেওয়া
            if (
                not href
                or href == "#"
                or href == base_url
                or "javascript:" in href
                or "category" in href
            ):
                continue

            full_page_url = (
                href if href.startswith("http") else urljoin(base_url, href)
            )

            if full_page_url in visited_urls:
                continue
            visited_urls.add(full_page_url)

            # থাম্বনেল ইমেজ বের করা
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

            # ডিটেইলস পেজে ঢুকে আসল ডাউনলোড লিংক নিয়ে আসা
            download_link = get_download_link_from_details(
                scraper, full_page_url, base_url
            )

            # যদি ডাউনলোড লিংক পাওয়া না যায়, তবে ডিটেইলস পেজের লিংকটিকে ব্যাকআপ হিসেবে রাখা
            if not download_link:
                download_link = full_page_url

            # শুধু ইমেজ এবং ডাউনলোড লিংক থাকলে যুক্ত করা হবে
            if download_link:
                final_data.append(
                    {"image": img_url, "download_link": download_link}
                )

        # Duplicate Links Clean UP
        seen = set()
        clean_data = []
        for item in final_data:
            if item["download_link"] not in seen:
                seen.add(item["download_link"])
                clean_data.append(item)

        final_data = clean_data

    except Exception as e:
        print(f"Scraping Error: {e}")

    # শুধুমাত্র image এবং download_link সহ JSON সেভ করা
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(final_data, f, ensure_ascii=False, indent=4)

    print(f"Successfully saved {len(final_data)} items to data.json")


if __name__ == "__main__":
    scrape_category()
