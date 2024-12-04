import os
import random
import json
import requests
from bs4 import BeautifulSoup
from slugify import slugify
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files.storage import default_storage
from django.utils.text import slugify

KSH_TO_USD_RATE = 0.00771
scrape_urls = os.getenv('SCRAPE_URL')


class Command(BaseCommand):
    help = "Scrape products from e-commerce and save them to the database."

    def convert_ksh_to_usd(self, price_str):
        try:
            price_numeric = float("".join(filter(str.isdigit, price_str)))
            return round(price_numeric * KSH_TO_USD_RATE, 2)
        except ValueError:
            return None

    def download_image(self, image_url, save_dir):
        try:
            response = requests.get(image_url, stream=True)
            response.raise_for_status()

            image_name = image_url.split("/")[-1]
            image_name = f'{image_name.split("?")[1]}.jpg'

            if not os.path.exists(save_dir):
                os.makedirs(save_dir)

            save_path = os.path.join(save_dir, image_name)

            base_name, ext = os.path.splitext(image_name)
            counter = 1
            while os.path.exists(save_path):
                save_path = os.path.join(
                    save_dir, f"{base_name}_{chr(96+counter)}{ext}")
                counter += 1

            with open(save_path, 'wb') as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)

            self.stdout.write(self.style.SUCCESS(
                f"Image saved to {save_path}"))
            return save_path

        except requests.RequestException as e:
            self.stderr.write(self.style.ERROR(
                f"Error downloading the image: {e}"))
            return None

    def extract_product_details_from_link(self, url):
        try:
            response = requests.get(f'{scrape_urls}/{url}')
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            description_div = soup.find(
                "div", class_="markup -mhm -pvl -oxa -sc")
            description = description_div.get_text(
                strip=True) if description_div else "Description not found"

            specifications_section = soup.find(
                "section", class_="card aim -mtm -fs16")
            sku = None
            specifications = {}
            if specifications_section:
                specification_items = specifications_section.find_all("li")
                for item in specification_items:
                    key = item.find("span", class_="-b")
                    if key:
                        key = key.text.strip().replace(":", "")
                        value = item.text.replace(key, "").strip()
                        if key == 'SKU':
                            sku = value
                        specifications[key] = value

            image_urls = []
            image_carousel = soup.find("div", class_="crs")
            if image_carousel:
                image_items = image_carousel.find_all("img")
                for img_tag in image_items:
                    img_url = img_tag.get('data-src')
                    if img_url:
                        image_urls.append(img_url)

            product_details = {
                "description": description,
                "sku": sku,
                "specifications": specifications,
                "images": image_urls
            }

            return product_details

        except requests.RequestException as e:
            self.stderr.write(self.style.ERROR(
                f"Error fetching the product page: {e}"))
            return {"description": "Error fetching description", "specifications": {}, "images": []}

    def scrape_products_from_page(self, url, save_dir):
        # sourcery skip: merge-dict-assign, move-assign-in-block
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            products = []
            for product in soup.find_all("article", class_="prd"):
                product_data = {}

                name_tag = product.find("h3", class_="name")
                title = name_tag.text.strip() if name_tag else "N/A"
                product_data["title"] = title
                if title:
                    product_data['slug'] = slugify(title)

                price_tag = product.find("div", class_="prc")
                if price_tag:
                    ksh_price = price_tag.text.strip()
                    product_data["price_ksh"] = ksh_price
                    product_data["price"] = self.convert_ksh_to_usd(ksh_price)
                else:
                    product_data["price"] = "N/A"

                img_tag = product.find("img", class_="img")
                if img_tag and img_tag.get("data-src"):
                    image_url = img_tag["data-src"]
                    if image_url:
                        image = self.download_image(image_url, save_dir)
                        product_data["image"] = image
                    else:
                        print('Product image not found')
                else:
                    product_data["image"] = None

                a_tag = product.find("a", class_="core")
                if a_tag:
                    product_data["brand"] = a_tag.get(
                        'data-ga4-item_brand', 'N/A')
                    product_data["category"] = a_tag.get(
                        'data-ga4-item_category', 'N/A')
                    href = a_tag.get('href')
                    if href:
                        product_details = self.extract_product_details_from_link(
                            href)
                        product_data["description"] = product_details["description"]
                        product_data["sku"] = product_details["sku"]
                        product_data["specifications"] = product_details["specifications"]
                        images_urls = product_details["images"]
                        product_data["images"] = [self.download_image(
                            i, save_dir) for i in images_urls if self.download_image(i, save_dir)]
                    else:
                        product_data["description"] = "No description available"
                        product_data["specifications"] = {}
                        product_data["images"] = []
                    product_data["stock"] = random.randint(1, 199)

                review_tag = product.find("div", class_="rev")
                product_data["reviews"] = review_tag.text.strip(
                ) if review_tag else "No reviews"

                products.append(product_data)

            next_page_tag = soup.find("a", {"aria-label": "Next"})
            next_page_url = next_page_tag["href"] if next_page_tag else None

            return products, next_page_url
        except requests.RequestException as e:
            self.stderr.write(self.style.ERROR(f"Error fetching the URL: {e}"))
            return [], None

    def scrape_all_products(self, base_url, save_dir):
        all_products = []
        next_page_url = base_url

        while next_page_url:
            self.stdout.write(f"Scraping page: {next_page_url}")
            products, next_page_url = self.scrape_products_from_page(
                next_page_url, save_dir)
            all_products.extend(products)

            if next_page_url and not next_page_url.startswith("http"):
                next_page_url = requests.compat.urljoin(
                    base_url, next_page_url)

        return all_products

    def handle(self, *args, **kwargs):
        start_url = os.getenv('SCRAPE_URL_PAGE')
        image_save_directory = "products"

        all_product_data = self.scrape_all_products(
            start_url, image_save_directory)

        output_file = "products.json"
        with open(output_file, "w", encoding="utf-8") as file:
            json.dump(all_product_data, file, ensure_ascii=False, indent=4)

        self.stdout.write(self.style.SUCCESS(
            f"Scraped data saved to {output_file}"))
        self.stdout.write(self.style.SUCCESS(
            f"Images URLs saved (no image downloading) to {image_save_directory}"))
