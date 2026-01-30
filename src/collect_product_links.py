import csv
import time
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from src.browser_setup import handle_cloudflare_if_present


SEARCH_URL = "https://www.autodoc.co.uk/spares-search?keyword=A2215420417"


def collect_product_links(page):
    """
    Collects all product detail page links from the AutoDoc search results
    by clicking the 'Load more' button until all products are loaded.
    """

    print("[INFO] Opening search page...")
    page.goto(SEARCH_URL, timeout=60000)

    handle_cloudflare_if_present(page)

    print("[INFO] Waiting for product listings to appear...")
    page.wait_for_selector("a.listing-item__name", timeout=60000)

    # --- Load more loop ---
    while True:
        try:
            load_more_button = page.locator("a[data-pagination-load-more]")
            if load_more_button.count() == 0:
                print("[INFO] No 'Load more' button found. All products should be loaded.")
                break

            print("[INFO] Clicking 'Load more' button...")
            load_more_button.first.click()

            # Give time for new products to load
            time.sleep(3)

        except PlaywrightTimeoutError:
            print("[WARNING] Timeout while trying to click 'Load more'.")
            break

        except Exception as e:
            print(f"[ERROR] Unexpected error while loading more products: {e}")
            break

    print("[INFO] Collecting product links from the page...")

    product_links = []
    seen_links = set()

    product_elements = page.locator("a.listing-item__name")
    total_found = product_elements.count()

    print(f"[INFO] Found {total_found} product elements.")

    for i in range(total_found):
        try:
            href = product_elements.nth(i).get_attribute("href")
            if href and href not in seen_links:
                product_links.append(href)
                seen_links.add(href)
        except Exception as e:
            print(f"[WARNING] Failed to read link at index {i}: {e}")

    return product_links


def save_links_to_csv(links, output_path):
    """
    Saves product links to a CSV file.
    """

    print(f"[INFO] Saving product links to {output_path}...")

    with open(output_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["product_url"])

        for link in links:
            writer.writerow([link])

    print("[SUCCESS] Product links saved successfully.")