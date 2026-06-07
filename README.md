# Google Careers Scraper

A lightweight, robust Python script powered by **Playwright** and **Pandas** to scrape job listings from the official Google Careers website. It automatically paginates through results, extracts key job details, handles unexpected rendering delays, and periodically backs up the collected data.

## Features

* **Automated Pagination:** Iterates through all available search result pages until no more jobs are found.
* **Smart Data Extraction:** Parses job titles, locations (handling multi-city listings), and minimum qualifications.
* **Resilience & Fault Tolerance:** Individual card parsing errors or network hiccups won't crash the entire script.
* **Data Backup:** Automatically saves a temporary CSV backup every 5 pages to prevent data loss.
* **Human-like Behavior:** Includes configurable delays to mimic human browsing and minimize the risk of triggering CAPTCHAs.

## Extracted Data Fields

The final dataset is exported as a CSV file containing the following columns:
* `Профессия` (Job Title)
* `Город / Локация` (City / Location)
* `Минимальная квалификация` (Minimum Qualifications)
* `Страница` (Page Number where the job was found)

---

## Prerequisites

Make sure you have Python 3.8+ installed on your system.

### Dependencies

Install the required Python packages using pip:

```bash
pip install playwright pandas
