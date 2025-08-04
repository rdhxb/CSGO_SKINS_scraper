import time
import pandas as pd
import os
from typing import List, Dict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import undetected_chromedriver as uc
from bs4 import BeautifulSoup

TARGET_URL = "https://csgo-skins.com"
CASE_CSV    = "data/cases.csv"
ITEM_CSV    = "data/items.csv"
EV_CSV      = "data/expected_values.csv"

def configure_driver() -> webdriver.Chrome:
    opts = webdriver.ChromeOptions()
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--start-maximized")
    return uc.Chrome(options=opts)

def wait_for_manual_cf_check(driver: webdriver.Chrome) -> None:
    driver.get(TARGET_URL)
    print("Complete Cloudflare check in browser, then press ENTER here.")
    input()
    try:
        WebDriverWait(driver, 15).until_not(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#cf-challenge-running"))
        )
    except TimeoutException:
        print("CF challenge still detected; continuing anyway")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    print("Page loaded:", driver.title)

def parse_case_entries(soup: BeautifulSoup) -> List[Dict]:
    entries = []
    for a in soup.find_all("a", class_="ContainersContainer_container", limit=6): # change the limit as needed max is 81, 6 is to show how it works
        name = a.find("h3", class_="ContainersContainer_name").text.strip()
        price = a.find("div", class_="ContainersContainer_price").text.strip()
        link = a["href"]
        entries.append({"name": name, "price": price, "link": link})
    return entries

def save_cases(entries: List[Dict]) -> List[str]:
    df = pd.DataFrame(entries)
    df.to_csv(CASE_CSV, mode="a", header=False, index=False)
    return [e["link"] for e in entries if e["link"].startswith("/case/")]

def fetch_boosted_links(driver: webdriver.Chrome, links: List[str]) -> List[str]:
    boosted = []
    for link in links:
        driver.get(TARGET_URL + link + "-boosted")
        soup = BeautifulSoup(driver.page_source, "html.parser")
        price_el = soup.select_one(".ContainerPrice.AppPage_price-value")
        if price_el:
            boosted.append(link + "-boosted")
            pd.DataFrame([{
                "name": link.split("/")[-1],
                "price": price_el.text.strip(),
                "link": link + "-boosted"
            }]).to_csv(CASE_CSV, mode="a", header=False, index=False)
    return boosted

def parse_price(val: str) -> float:
    return float(val.replace("zł","").replace("€","").strip() or 0)

def parse_odds(val: str) -> float:
    return float(val.replace("%","").strip() or 0) / 100

def extract_items(soup: BeautifulSoup, boosted: bool) -> List[Dict]:
    selector = (
        "div.ContainerGroupedItem--boost-mode"
        if boosted else "div.ContainerGroupedItem.item_item"
    )
    items = []

    for block in soup.select(selector):
        name = block.select_one(".ContainerGroupedItem_name").text.strip()
        for row in block.select("table.chances_table tr"):
            cols = row.find_all("td")
            if len(cols) >= 4:
                items.append({
                    "name": name,
                    "price": cols[1].find("span").text.strip(),
                    "odds": cols[3].text.strip()
                })
    return items

def process_case(driver: webdriver.Chrome, link: str) -> None:
    full_url = TARGET_URL + link
    driver.get(full_url)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    boosted = "boosted" in link

    items = extract_items(soup, boosted)
    total_ev = 0.0
    rows = []
    for it in items:
        price = parse_price(it["price"])
        odds = parse_odds(it["odds"])
        ev = price * odds
        total_ev += ev
        print(f"{it['name']}: {price} zl, {it['odds']}, EV={ev:.2f} zl")
        rows.append({
            "Item Name": it["name"],
            "Item Price": price,
            "Item Odds": it["odds"],
            "Expected Value": ev,
            "Case Name": link.split("/")[-1].replace("-", " ").title()
        })
    pd.DataFrame(rows).to_csv(ITEM_CSV, mode="a", header=False, index=False)

    case_price = soup.select_one(".ContainerHeader_price")
    case_price = case_price.text.strip() if case_price else "N/A"
    print(f"Total EV for {link}: {total_ev:.2f} zl")
    pd.DataFrame([{
        "Case Link": link,
        "Total Expected Value": total_ev,
        "Case Name": link.split("/")[-1].replace("-", " ").title()
    }]).to_csv(EV_CSV, mode="a", header=False, index=False)
    time.sleep(1)

def init_csv_files() -> None:
    """
    Clear out existing CSVs and rewrite only the header row.
    """
    pd.DataFrame(columns=["case_name", "case_price", "case_link"]).to_csv(CASE_CSV, index=False)
    pd.DataFrame(
        columns=[
            "Item Name",
            "Item Price",
            "Item Odds",
            "Expected Value",
            "Case Name",
        ]
    ).to_csv(ITEM_CSV, index=False)
    pd.DataFrame(
        columns=["case_link", "case_total_expected_value", "case_name"]
    ).to_csv(EV_CSV, index=False)

def main():
    driver = configure_driver()
    try:
        wait_for_manual_cf_check(driver)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        base_links = save_cases(parse_case_entries(soup))
        boosted = fetch_boosted_links(driver, base_links)
        for link in base_links + boosted:
            process_case(driver, link)
    finally:
        driver.quit()
        print("Done. Browser closed.")

if __name__ == "__main__":
    # Reset all CSVs (keep only headers) before starting
    init_csv_files()
    main()

    from marge import merge_csv_files
    from calculate_diff import calculate_diff



    merge_csv_files()
    calculate_diff()