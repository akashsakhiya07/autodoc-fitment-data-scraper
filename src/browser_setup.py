from playwright.sync_api import sync_playwright
import time
import os


def launch_browser(headless=False):
    """
    Launches a persistent Chromium browser context.
    This helps bypass aggressive Cloudflare checks by reusing
    a real browser profile (cookies, storage, session).
    """

    user_data_dir = os.path.join(os.getcwd(), "user_data")

    playwright = sync_playwright().start()

    context = playwright.chromium.launch_persistent_context(
        user_data_dir=user_data_dir,
        headless=headless,
        viewport=None,
        args=[
            "--start-maximized",
            "--disable-blink-features=AutomationControlled"
        ]
    )

    page = context.new_page()

    return playwright, context, page

import time


def handle_cloudflare_if_present(page):
    """
    Detects Cloudflare verification and safely waits
    for the page to stabilize after manual verification.
    """

    try:
        print("\n[DEBUG] Current URL:", page.url)
        print("[DEBUG] Page title:", page.title())
    except Exception:
        print("[DEBUG] Page is navigating, unable to read title right now.")

    page_content = page.content().lower()

    if (
        "cloudflare" in page_content
        or "verify you are human" in page_content
        or "just a moment" in page_content
    ):
        print("\n[!] Cloudflare verification detected.")
        print("[!] Please complete the verification manually in the browser.")
        print("[!] Wait until the real AutoDoc page fully loads.")

        input("[!] After the page loads, press ENTER here...")

        print("[INFO] Waiting for page to stabilize after verification...")

        try:
            page.wait_for_load_state("domcontentloaded", timeout=30000)
            time.sleep(3)
        except Exception:
            print("[WARNING] Page load wait timed out. Continuing anyway.")

        # Safe re-check (wrapped to avoid crash)
        try:
            final_title = page.title()
            print("[DEBUG] Page title after verification:", final_title)

            if "just a moment" in final_title.lower():
                print("[ERROR] Still on Cloudflare page.")
                print("[HINT] Close the script and run it again. Profile is now saved.")
            else:
                print("[SUCCESS] Cloudflare verification passed successfully.")

        except Exception:
            print("[WARNING] Page title could not be read after verification.")
            print("[INFO] This usually means the page is still redirecting.")