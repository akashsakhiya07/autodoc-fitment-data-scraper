# AutoDoc Part Fitment Data Scraper

## Project Overview
This project was built to scrape **OEM part numbers** and their **vehicle compatibility details** from the AutoDoc website based on a given search term.  
The client’s requirement was very specific:  
- For each searched part number, collect **all OEM numbers** listed on the product page  
- Collect **all compatible vehicles** (across different car brands)  
- Deliver the data in a **clean, Excel-friendly CSV format** with no missing or mixed data  

The main challenge was that the website is highly dynamic and protected by Cloudflare, so a simple scraper would not work reliably.

---

## What the Client Needed
- Start from a search URL (example: part number search)
- Handle multiple products returned by the search (53 products in this case)
- For each product:
  - Extract all OEM numbers (sometimes a few, sometimes more than 100)
  - Extract all compatibility entries across multiple car brands
- Output format had to be **column-aligned**, so the client could directly open it in Excel and understand it without post-processing

---

## Output Format Logic
The final CSV format strictly follows this rule:

- Columns:
  - `OEM Number`
  - `Compatibility`
- Number of rows per product = **max(OEM count, Compatibility count)**
- If one column has fewer values:
  - The remaining rows are left blank in that column
- This ensures:
  - No data is lost
  - Excel view remains readable and consistent
  - OEM numbers and compatibility data are never merged incorrectly

Each product is saved as a **separate CSV file**, making it easy for the client to review or share individual results.

---

## Website Behavior & Data Loading
AutoDoc does not load all data at once:
- Search results use a **“Load more”** system instead of full page reloads
- Product pages load data dynamically with JavaScript
- OEM numbers sometimes appear partially and require clicking a **“More”** button
- Compatibility data is hidden under expandable brand sections (only one brand opens at a time)

All of these behaviors were handled carefully using explicit waits, visibility checks, and controlled retries.

---

## Cloudflare Challenges
The biggest obstacle was **Cloudflare bot protection**:
- Requests were blocked when using basic HTTP scraping
- Selenium often got stuck on verification pages
- Even after manual verification, sessions were sometimes invalidated

### How This Was Solved
- Switched from Selenium to **Playwright**
- Used a real browser context with persistent user data
- Allowed manual Cloudflare verification when required
- Added safe retry logic only where it made sense (for dynamic UI elements, not static ones)

This approach made the scraper stable and repeatable without abusing retries or guessing page states.

---

## Why Playwright Instead of Selenium
Playwright was chosen because:
- It handles modern, JavaScript-heavy websites more reliably
- Browser context and session handling is more predictable
- It works better with Cloudflare-protected sites
- Element visibility and interaction checks are more precise

For this project, Playwright proved to be the safer and more production-ready choice.

---

## Tech Stack
- Python
- Playwright (browser automation)
- CSV for structured output
- Virtual environment for isolation

---

## Result
- All 53 products scraped successfully
- No missing OEM numbers
- No missing compatibility entries
- Output matches the exact format requested by the client
- Ready to be shared directly with non-technical users

This project reflects a real-world scraping scenario where handling dynamic content and anti-bot protection is just as important as extracting the data itself.