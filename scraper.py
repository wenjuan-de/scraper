from chausson_scraper import ChaussonScraper

if __name__ == "__main__":
    # Initialize the scraper
    sc = ChaussonScraper(input_file="input/input.csv")

    try:
        # Setup Selenium driver
        sc.setup_driver()

        # Wait for user manual setup (choose store, set prices)
        sc.wait_for_user_setup()

        # 4Start scraping all articles
        sc.scrape_articles()

        # Save results to Excel
        sc.save_output()

    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}\n")

    finally:
        # 6close driver
        sc.close_driver()
        print("\n✅ Scraper finished and driver closed.")

