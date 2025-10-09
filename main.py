from chausson_scraper import ChaussonScraper
import sys, io

# ✅ Force stdout to use UTF-8 safely (avoids crash even if special chars appear)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

if __name__ == "__main__":
    # Initialize the scraper
    sc = ChaussonScraper(input_file="input/input.csv")

    try:
        # Setup Selenium driver
        sc.setup_driver()

        # Wait for user manual setup (choose store, set prices)
        sc.wait_for_user_setup()

        # Start scraping all articles
        sc.scrape_articles()

        # Save results to Excel
        sc.save_output()

    except Exception as e:
        print(f"[ERROR] An unexpected error occurred: {e}")

    finally:
        # Always close the driver, even if an error occurred
        sc.close_driver()
        print("[OK] Scraper finished and driver closed.")

