import csv
import os
import time

from src.browser_setup import launch_browser
from src.scrape_product_data import scrape_product_page


LINKS_FILE = "output/product_links.csv"
OUTPUT_DIR = "output/final_data"


def read_product_links(csv_path):
    """
    Reads product links from CSV file and returns them as a list.
    """

    links = []

    with open(csv_path, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            links.append(row["product_url"])

    return links


def save_product_csv(rows, output_path):
    """
    Saves OE number and compatibility rows into a CSV file.
    """

    with open(output_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["OEM Number", "Compatibility"])

        for oe, compatibility in rows:
            writer.writerow([oe, compatibility])


def main():
    print("[INFO] Starting product data scraping pipeline...")

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    product_links = read_product_links(LINKS_FILE)
    total_products = len(product_links)

    print(f"[INFO] Total product links to process: {total_products}")

    playwright, context, page = launch_browser(headless=False)

    for index, product_url in enumerate(product_links, start=1):
        print("\n" + "=" * 60)
        print(f"[INFO] Processing product {index} of {total_products}")

        try:
            rows = scrape_product_page(page, product_url)

            if not rows:
                print("[WARNING] No data extracted for this product.")
                continue

            output_file = os.path.join(
                OUTPUT_DIR,
                f"product_{index}.csv"
            )

            save_product_csv(rows, output_file)

            print(f"[SUCCESS] Data saved to {output_file}")

            # Small delay to keep things human-like
            time.sleep(2)

        except Exception as e:
            print(f"[ERROR] Failed to process product {index}: {e}")

    print("\n[INFO] All products processed.")
    input("Press ENTER to close the browser...")

    context.close()
    playwright.stop()


if __name__ == "__main__":
    main()
