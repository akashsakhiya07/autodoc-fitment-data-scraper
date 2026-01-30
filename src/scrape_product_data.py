import time
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from src.browser_setup import handle_cloudflare_if_present

MAX_RETRIES = 3

def scrape_product_page(page, product_url):
    """
    Scrapes OE numbers and Compatibility data from a single AutoDoc product page.
    Uses retry logic to ensure full data is collected.
    """

    print(f"\n[INFO] Opening product page:\n{product_url}")
    page.goto(product_url, timeout=60000)
    handle_cloudflare_if_present(page)

    # -------------------------------------------------
    # STEP 1: SCRAPE OE NUMBERS (VISIBLE-MORE ONLY)
    # -------------------------------------------------
    
    oe_numbers = []
    
    print("[INFO] Scraping OE numbers...")
    
    page.wait_for_selector("div.product-oem", timeout=20000)
    
    more_button = page.locator("span[data-show-more-btn]")
    
    # IMPORTANT FIX:
    # More button is considered valid ONLY if it is visible
    has_visible_more_button = (
        more_button.count() > 0 and more_button.first.is_visible()
    )
    
    max_attempts = MAX_RETRIES if has_visible_more_button else 1
    
    for attempt in range(1, max_attempts + 1):
        try:
            if has_visible_more_button:
                print(f"[INFO] Clicking OE 'More' button (attempt {attempt})...")
                more_button.first.click()
                time.sleep(2)
    
            oe_numbers.clear()
    
            for el in page.locator("a.product-oem__link").all():
                oe_numbers.append(el.inner_text().strip())
    
            for el in page.locator("span.product-oem__text").all():
                oe_numbers.append(el.inner_text().strip())
    
            if oe_numbers:
                print(f"[SUCCESS] Found {len(oe_numbers)} OE entries.")
                break
    
        except Exception as e:
            print(f"[WARNING] OE scrape failed on attempt {attempt}: {e}")
            time.sleep(2)
    
    if not oe_numbers:
        print("[ERROR] Failed to collect OE numbers.")
        return []

    # -------------------------------------------------
    # STEP 2: SCRAPE COMPATIBILITY (WITH PER-BRAND RETRIES)
    # -------------------------------------------------

    compatibilities = []

    print("[INFO] Scraping compatibility data...")

    brand_headers = page.locator("a.product-info-block__item-title")
    brand_count = brand_headers.count()

    print(f"[INFO] Found {brand_count} brand sections.")

    for b in range(brand_count):
        brand = brand_headers.nth(b)
        brand_name = brand.inner_text().strip()

        print(f"[INFO] Processing brand: {brand_name}")

        success = False

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                brand.click()
                time.sleep(1)

                target_id = brand.get_attribute("data-target")
                if not target_id:
                    raise Exception("Missing data-target attribute")

                panel = page.locator(f"ul{target_id}")
                panel.wait_for(state="visible", timeout=15000)

                items = panel.locator(
                    "span.product-info-block__item-list__title"
                )

                count = items.count()
                if count == 0:
                    raise Exception("Compatibility list is empty")

                print(f"[SUCCESS]  ↳ Found {count} compatibility items")

                for i in range(count):
                    text = items.nth(i).inner_text().strip()
                    if text:
                        compatibilities.append(text)

                success = True
                break

            except Exception as e:
                print(
                    f"[WARNING] Brand '{brand_name}' attempt {attempt} failed: {e}"
                )
                time.sleep(2)

        if not success:
            print(
                f"[ERROR] Skipping brand '{brand_name}' after retries."
            )

    if not compatibilities:
        print("[ERROR] No compatibility data collected.")
        return []

    # -------------------------------------------------
    # STEP 3: BUILD FINAL ROWS (FULL EXCEL LOGIC)
    # -------------------------------------------------
    
    results = []
    
    total_rows = max(len(oe_numbers), len(compatibilities))
    
    for i in range(total_rows):
        oe_value = oe_numbers[i] if i < len(oe_numbers) else ""
        compatibility_value = compatibilities[i] if i < len(compatibilities) else ""
    
        results.append((oe_value, compatibility_value))
    
    print(f"[SUCCESS] Total rows collected from this product: {len(results)}")
    return results