import os
from time import sleep
from datetime import datetime
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class ChaussonScraper:
    def __init__(self, input_file, output_dir='output'):
        # Normalize input/output paths
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.input_file = os.path.join(self.base_dir, input_file)
        self.output_dir = os.path.join(self.base_dir, output_dir)

        # Load articles and prepare output folder
        self.articles = self.load_input_articles()
        self.output_folder = self.create_output_folder()
        self.driver = None

    def load_input_articles(self):
        input_articles = pd.read_csv(self.input_file, encoding="utf-8", sep=";", dtype="str")
        input_articles["code_article"] = input_articles["code_article"].astype("str").str.zfill(7)
        return input_articles.to_dict("records")

    def create_output_folder(self):
        output_folder_name = f"Scraping_Chausson_{datetime.now().strftime('%Y%m%d-%Hh%M.%S')}"
        output_folder = os.path.join(self.output_dir, output_folder_name)
        os.makedirs(os.path.join(output_folder, "screenshots"), exist_ok=True)
        return output_folder

    def setup_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--log-level=3")
        options.add_argument("--disable-search-engine-choice-screen")

        # ✅ Use your existing local chromedriver
        chromedriver_path = os.path.join(self.base_dir, "chromedriver", "chromedriver.exe")

        # Check if it exists before running
        if not os.path.exists(chromedriver_path):
            raise FileNotFoundError(f"❌ ChromeDriver not found at {chromedriver_path}")

        service = Service(chromedriver_path)
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.maximize_window()
        print(f"✅ ChromeDriver loaded from: {chromedriver_path}")

    def close_driver(self):
        if self.driver:
            self.driver.quit()

    def wait_for_user_setup(self):
        base_url = "https://www.chausson.fr/"
        self.driver.get(base_url)
        input("\n******* Please configure the site (select the appropriate store, display prices excluding tax). Press any key to start scraping when ready\n >>>")
        print("-" * 100)

    def scrape_article(self, article, sleep_time: float = 10.0):
        try:
            self.driver.get(article["url_chausson"])
            sleep(sleep_time)

            if self.driver.title == "Cette page n'a pas été trouvée":
                return {
                    "product_reference_code": "Invalide URL",
                    "depot_selected": "N/A",
                    "product_name": "N/A",
                    "product_price": "N/A",
                    "product_unit": "N/A",
                }

            product_price = self.driver.find_element(By.CSS_SELECTOR, 'div.prix-principal price').text.split("€")[0].strip()
            product_name = self.driver.find_element(By.TAG_NAME, 'h1').text
            product_unit = self.driver.find_element(By.CSS_SELECTOR, 'div.qty-unit').text
            product_reference_code = self.driver.find_element(By.CSS_SELECTOR, '.product-reference.mb-1').text.split(" ")[2]
            depot_selected = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.agence-selected'))
            ).text.split(" ")[0]

            return {
                "product_reference_code": product_reference_code,
                "depot_selected": depot_selected,
                "product_name": product_name,
                "product_price": product_price,
                "product_unit": product_unit,
            }

        except Exception as e:
            return {
                "product_reference_code": "error",
                "depot_selected": "error",
                "product_name": "error: " + str(e),
                "product_price": "error",
                "product_unit": "error",
            }

    def save_screenshot(self, code_article, product_name):
        screenshot_path = os.path.join(self.output_folder, "screenshots", f"{code_article} - {product_name}.png")
        self.driver.save_screenshot(screenshot_path)

    def scrape_articles(self):
        for article in self.articles:
            scraped_data = self.scrape_article(article)
            article.update(scraped_data)
            self.save_screenshot(article["code_article"], article["product_name"])
            print(f'{article["code_article"]} - {article["product_name"]} <---------- {"Scraped successfully!" if article["product_reference_code"] != "Invalide URL" else "error"} !')

    def save_output(self):
        output_file = os.path.join(self.output_folder, f"Résultat_Scraping_Chausson_{datetime.now().strftime('%Y%m%d-%Hh%M.%S')}.xlsx")
        output_df = pd.DataFrame(self.articles)
        output_df.to_excel(output_file, index=False)
        print(f"Results saved to {self.output_folder}")






