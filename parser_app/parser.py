# -*- coding: utf-8 -*-
import os
import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

class ELibraryParser:
    def __init__(self):
        self.driver = None
    
    def setup_driver(self):
        """Настройка WebDriver"""
        opts = Options()
        opts.binary_location = r"C:\Users\basa\AppData\Local\Yandex\YandexBrowser\Application\browser.exe"
        opts.add_argument("--headless")
        opts.add_argument("--disable-gpu")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-blink-features=AutomationControlled")
        opts.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        driver_path = os.path.join(os.path.dirname(__file__), 'chromedriver.exe')
        
        if not os.path.exists(driver_path):
            raise Exception(f"chromedriver.exe не найден: {driver_path}")
        
        self.driver = webdriver.Chrome(
            service=Service(driver_path),
            options=opts
        )
        return self.driver
    
    def parse_article(self, url):
        """Парсинг статьи с eLibrary"""
        if not self.driver:
            self.setup_driver()
        
        try:
            print(f"📄 Открываю URL: {url}")
            self.driver.get(url)
            time.sleep(5)  # Увеличенное время загрузки
            
            # Проверка на капчу
            if "Тест Тьюринга" in self.driver.page_source:
                print("⚠️ Обнаружена капча!")
                return None
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            full_text = soup.get_text(' ', strip=True)
            text_clean = re.sub(r'[¹²³⁴⁵⁷⁹]', '', full_text)
            
            print(f"📄 Длина страницы: {len(full_text)} символов")
            
            data = {
                'title': '', 'authors': [], 'year': None,
                'place': '', 'work_type': '', 'pages': None, 'url': url
            }
            
            # Название - пробуем несколько способов
            h1 = soup.find('h1')
            if h1:
                data['title'] = h1.get_text(strip=True)
                print(f"✓ Название найдено: {data['title'][:50]}...")
            
            if not data['title']:
                meta = soup.find('meta', property='og:title')
                if meta and meta.get('content'):
                    data['title'] = meta['content']
                    print(f"✓ Название из meta: {data['title'][:50]}...")
            
            if not data['title']:
                print("❌ Название НЕ найдено!")
                print(f"   Первые 500 символов: {full_text[:500]}")
                return None
            
            # Авторы
            title_pos = text_clean.find(data['title'])
            snippet = text_clean[title_pos:title_pos+2000] if title_pos != -1 else text_clean[:2500]
            
            pattern = r'([А-ЯЁ]{3,}\s+[А-ЯЁ]\.[А-ЯЁ]\.)'
            authors = re.findall(pattern, snippet)
            clean_authors = [a.strip().rstrip(',').rstrip('.') for a in authors 
                           if len(a) > 8 and '.' in a and 'ГОД' not in a and 'ТИП' not in a]
            data['authors'] = list(set(clean_authors))[:10]  # Убираем дубли
            
            if data['authors']:
                print(f"✓ Авторы найдены ({len(data['authors'])}): {', '.join(data['authors'][:3])}")
            else:
                print("⚠️ Авторы НЕ найдены")
                print(f"   Текст после названия: {snippet[:300]}")
            
            # Год
            year_match = re.search(r'Год издания:\s*(\d{4})', text_clean)
            if year_match:
                data['year'] = int(year_match.group(1))
                print(f"✓ Год: {data['year']}")
            
            # Тип работы
            type_match = re.search(r'Тип:\s*([^\n\r,;]+?)(?:\s+(?:Язык|Источник):|$)', text_clean)
            if type_match:
                data['work_type'] = type_match.group(1).strip()
                print(f"✓ Тип: {data['work_type']}")
            
            # Страницы
            pages_match = re.search(r'(?:Страницы:\s*|С\.?\s*)(\d+)(?:\s*с\.?)?', text_clean)
            if pages_match:
                data['pages'] = int(pages_match.group(1))
                print(f"✓ Страниц: {data['pages']}")
            
            # Место издания
            cities = ['Северск', 'Москва', 'Санкт-Петербург', 'Казань']
            source_match = re.search(r'ИСТОЧНИК:[\s\S]{0,400}', text_clean)
            if source_match:
                for city in cities:
                    if city in source_match.group(0):
                        data['place'] = city
                        print(f"✓ Место: {data['place']}")
                        break
            
            return data
            
        except Exception as e:
            print(f"❌ Ошибка парсинга: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
        
        finally:
            if self.driver:
                self.driver.quit()