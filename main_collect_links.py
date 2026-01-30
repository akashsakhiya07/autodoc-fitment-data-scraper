from src.browser_setup import launch_browser
from src.collect_product_links import collect_product_links, save_links_to_csv

OUTPUT_FILE = "output/product_links.csv"

playwright, context, page = launch_browser(headless=False)

links = collect_product_links(page)
save_links_to_csv(links, OUTPUT_FILE)

input("\nPress ENTER to close the browser...")
context.close()
playwright.stop()