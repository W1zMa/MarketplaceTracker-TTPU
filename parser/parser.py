from unittest import result
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium_stealth import stealth
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import json
import time

class SaveFromBan:
    def init_webdriver():
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        stealth(driver,
                languages=["ru-RU", "ru"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Google Inc.",
                renderer="Google Inc.",
                fix_hairline=True,
                )
        return driver

    def quit_webdriver(self):
        self.driver.quit()

class uzum(SaveFromBan):
    def __init__(self):
        self.driver = SaveFromBan.init_webdriver()
        
    def scroll_down(self, deep = 10, ):
        for _ in range(deep):
            self.driver.execute_script('window.scrollBy(0, 500)')
            time.sleep(0.1)
        
    def get_products(self):
        self.driver.get("https://uzum.uz/ru")
        self.driver.fullscreen_window()
        time.sleep(5)
        self.scroll_down(15)
        time.sleep(3)
        result = []
        html = self.driver.page_source
        main_page_html = BeautifulSoup(html, "html.parser")
        top_content = main_page_html.find_all("li", class_ = "category promo-category-link")
        static_links = [
            "https://uzum.uz/ru/category/tovary-nedeli--895",
            "https://uzum.uz/ru/promo/baby"
        ]
        
        for i, top_item in enumerate(top_content):
            span_tag = top_item.find("span", class_ = "title")
            if span_tag:
                name = span_tag.text.strip()
                if i < len(static_links):
                    href = static_links[i]
                else:
                    href = "https://uzum.uz/ru/category/tovary-nedeli--895" 
                
                result.append({
                    "title": name,
                    "href": href
                })
        content = main_page_html.find_all("li", class_ = "category")
        for item in content:
            a_tag = item.find("a", class_="ui-link category__body slightly transparent")
            if a_tag:
                name = a_tag.text.strip()
                href = a_tag.get("href")
                #print(f"{name} -> https://uzum.uz{href}")
                result.append({
                    "title": name,
                    "href": f"https://uzum.uz{href}"
                })
        with open("result.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

class yandex(SaveFromBan):
    def __init__(self):
        self.driver = SaveFromBan.init_webdriver()
    def get_products(self):
        
        self.driver.get("https://yandex.ru")
        time.sleep(10)

u = uzum()
u.get_products()
input("Нажми Enter, чтобы закрыть браузер...")
u.quit_webdriver()