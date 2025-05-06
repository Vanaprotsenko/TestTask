import requests
from bs4 import BeautifulSoup
import json
import re
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from django.conf import settings
from django.db import IntegrityError
from .models import Car

logger = logging.getLogger('scraper')


class AutoRiaScraper:
    def __init__(self, start_url=None):
        self.start_url = start_url or settings.SCRAPER_START_URL

    def run(self):
        logger.info("Starting AutoRia scraper")
        all_cars = []
        page_count = 1

        try:
            has_more_pages = True

            while has_more_pages:
                current_url = self.start_url if page_count == 1 else f"{self.start_url}?page={page_count}"

                logger.info(f"Scraping page {page_count}: {current_url}")

                cars, has_content = scrape_page(current_url)

                if cars:
                    all_cars.extend(cars)
                    logger.info(f"Added {len(cars)} cars. Total: {len(all_cars)}")

                    self._save_cars_to_db(cars)

                if not has_content:
                    logger.info("No content found on page, ending scraping")
                    has_more_pages = False
                else:
                    page_count += 1

            self._save_to_json(all_cars)

            logger.info(f"Scraping complete. Scraped {len(all_cars)} cars.")
            return len(all_cars)

        except Exception as e:
            logger.error(f"Error during scraping: {e}")
            return 0

    def _save_cars_to_db(self, cars):
        for car_data in cars:
            try:
                Car.objects.update_or_create(
                    url=car_data['url'],
                    defaults={
                        'title': car_data['title'],
                        'price_usd': car_data['price_usd'],
                        'odometer': car_data['odometer'],
                        'username': car_data['username'],
                        'phone_number': car_data['phone_number'],
                        'image_url': car_data['image_url'],
                        'images_count': car_data['images_count'],
                        'car_number': car_data['car_number'],
                        'car_vin': car_data['car_vin'],
                    }
                )
            except IntegrityError:
                logger.warning(f"Car with URL {car_data['url']} already exists, skipping.")
            except Exception as e:
                logger.error(f"Error saving car to database: {e}")

    def _save_to_json(self, cars):
        try:
            import json
            import os
            from django.conf import settings

            dumps_dir = settings.DUMPS_DIR
            os.makedirs(dumps_dir, exist_ok=True)

            filename = os.path.join(dumps_dir, f"autoria_cars_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(cars, f, ensure_ascii=False, indent=2)

            logger.info(f"Car data saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving cars to JSON: {e}")


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def clean_phone_number(phone):
    return re.sub(r"[^\d+]", "", phone) if phone else ""


def parse_odometer(odometer):
    if not odometer:
        return 0
    odometer = odometer.replace(" тис.", "").strip()
    try:
        return int(float(odometer) * 1000)
    except ValueError:
        return 0


def get_phone_number(soup):
    phone_div = soup.select_one("div.phone_block")
    if phone_div:
        phone = phone_div.get_text(strip=True)
        return clean_phone_number(phone)

    phone_elements = soup.select(".phones_item, .phones .item")
    for elem in phone_elements:
        phone = clean_phone_number(elem.get_text(strip=True))
        if phone:
            return phone

    phone_attrs = soup.select("[data-phone-number]")
    for elem in phone_attrs:
        if "data-phone-number" in elem.attrs:
            return clean_phone_number(elem["data-phone-number"])

    scripts = soup.select("script")
    for script in scripts:
        if script.string:
            phone_match = re.search(r'"phone":\s*"([^"]+)"', script.string)
            if phone_match:
                return clean_phone_number(phone_match.group(1))

    return ""


def get_car_number(soup):
    car_number_elem = soup.select_one("span.state-num")
    if car_number_elem:
        car_number = car_number_elem.get_text(strip=True)
        if car_number:
            return car_number

    number_elements = soup.select(".state-num, .number-plate, .plate-number, [data-plate]")
    for elem in number_elements:
        car_number = elem.get_text(strip=True)
        if car_number:
            return car_number

    number_attrs = soup.select("[data-plate], [data-number]")
    for elem in number_attrs:
        if "data-plate" in elem.attrs:
            return elem["data-plate"]
        elif "data-number" in elem.attrs:
            return elem["data-number"]

    scripts = soup.select("script")
    for script in scripts:
        if script.string:
            number_match = re.search(r'"plateNumber":\s*"([^"]+)"', script.string)
            if number_match:
                return number_match.group(1)

            number_match = re.search(r'"state_number":\s*"([^"]+)"', script.string)
            if number_match:
                return number_match.group(1)

    text_elements = soup.select("div.description-car, div.auto-wrap, div.autoinfo")
    for elem in text_elements:
        text = elem.get_text()
        car_num_match = re.search(r'[A-ZА-Я]{2}\d{4}[A-ZА-Я]{2}', text)
        if car_num_match:
            return car_num_match.group(0)

    return ""


def get_car_vin(soup):
    car_vin_elem = soup.select_one("span.vin-code")
    if car_vin_elem:
        vin = car_vin_elem.get_text(strip=True)
        if vin:
            return vin

    vin_elements = soup.select(".vin span, .label-vin, span[data-vin]")
    for elem in vin_elements:
        vin = elem.get_text(strip=True)
        if vin:
            return vin

    vin_attrs = soup.select("[data-vin], [data-code]")
    for elem in vin_attrs:
        if "data-vin" in elem.attrs:
            return elem["data-vin"]
        elif "data-code" in elem.attrs:
            return elem["data-code"]

    scripts = soup.select("script")
    for script in scripts:
        if script.string:
            vin_match = re.search(r'"vin":\s*"([A-Z0-9]+)"', script.string)
            if vin_match:
                return vin_match.group(1)

    return ""


def scrape_car_page(car_url):
    try:
        logger.debug(f"Scraping car page: {car_url}")
        response = requests.get(car_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.select_one("h1.head").get_text(strip=True) if soup.select_one("h1.head") else ""
        price_usd = soup.select_one("div.price_value > strong")
        price_usd = int(re.sub(r"[^\d]", "", price_usd.get_text(strip=True))) if price_usd else 0

        odometer_elem = soup.select_one("div.base-information > span")
        odometer = parse_odometer(odometer_elem.get_text(strip=True) if odometer_elem else "")

        username = soup.select_one("div.seller_info_name")
        username = username.get_text(strip=True) if username else ""

        phone_number = get_phone_number(soup)

        image_url = soup.select_one("div.photo-620x465 img")
        image_url = image_url["src"] if image_url and "src" in image_url.attrs else ""

        images_count = len(soup.select("div.photo-620x465 img"))

        car_number = get_car_number(soup)
        car_vin = get_car_vin(soup)

        return {
            "url": car_url,
            "title": title,
            "price_usd": price_usd,
            "odometer": odometer,
            "username": username,
            "phone_number": phone_number,
            "image_url": image_url,
            "images_count": images_count,
            "car_number": car_number,
            "car_vin": car_vin,
            "datetime_found": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error scraping {car_url}: {e}")
        return None


def scrape_page(url):
    try:
        logger.info(f"Scraping search page: {url}")
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        car_cards = soup.select("section.ticket-item")
        if not car_cards:
            car_cards = soup.select("div.content-bar")

        car_data = []
        car_urls = []

        logger.info(f"Found {len(car_cards)} car cards")

        for card in car_cards:
            title_element = card.select_one(
                "div.content > div.head-ticket > div.item.ticket-title > a > span.blue.bold")
            if not title_element:
                title_element = card.select_one("a.address span.blue")
                if not title_element:
                    title_element = card.select_one("span.blue.bold")

            title = title_element.get_text(strip=True) if title_element else 'Название не найдено'

            car_link = card.select_one("a.address")
            if not car_link:
                car_link = card.select_one("a.m-link-ticket")

            if car_link and 'href' in car_link.attrs:
                car_url = car_link['href']
                if not car_url.startswith('http'):
                    car_url = 'https://auto.ria.com' + car_url
                car_urls.append((car_url, title))

        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(lambda x: scrape_car_page(x[0]), car_urls))

        for i, result in enumerate(results):
            if result:
                result['title'] = car_urls[i][1]
                car_data.append(result)

        if len(car_cards) == 0:
            logger.info("No car cards found on page, probably reached the end")
            return car_data, False

        return car_data, True
    except Exception as e:
        logger.error(f"Error parsing page {url}: {e}")
        return [], False
