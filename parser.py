from playwright.sync_api import sync_playwright
import pandas as pd
import time

def scrape_entire_google_careers():
    with sync_playwright() as p:
        # Запуск браузера в видимом режиме для контроля процесса.
        # Для работы в фоновом режиме измените на headless=True.
        browser = p.chromium.launch(headless=False, args=["--start-maximized"])
        context = browser.new_context(no_viewport=True)
        page = context.new_page()
        
        jobs_data = []
        current_page = 1
        
        print("Запуск сбора вакансий с Google Careers...")
        
        while True:
            url = f"https://www.google.com/about/careers/applications/jobs/results?page={current_page}"
            print(f"\n--- Обработка страницы {current_page} ---")
            
            try:
                page.goto(url, wait_until="networkidle", timeout=60000)
                page.wait_for_timeout(2000)  # Пауза для корректного рендеринга элементов
            except Exception as e:
                print(f"Ошибка загрузки страницы {current_page}: {e}. Повторная попытка...")
                time.sleep(5)
                continue
            
            # Поиск карточек вакансий по возможным селекторам
            cards = page.locator("li.vO77gd, li[role='listitem']").all()
            if not cards:
                cards = page.locator("div.D6SuYc, li").all()
            
            # Отбор только валидных карточек, содержащих заголовок h3
            valid_cards = []
            for card in cards:
                try:
                    if card.is_visible() and card.locator("h3").count() > 0:
                        valid_cards.append(card)
                except:
                    continue
            
            # Если на странице нет валидных вакансий, прерываем цикл (дойли до конца списка)
            if not valid_cards:
                print(f"На странице {current_page} вакансии не найдены. Сбор данных завершен.")
                break
                
            print(f"Найдено вакансий на странице: {len(valid_cards)}")
            
            for index, card in enumerate(valid_cards):
                try:
                    # 1. Извлечение названия должности
                    title = card.locator("h3").first.inner_text().strip()
                    
                    # Разделение текста карточки на строки для последующего парсинга
                    lines = [line.strip() for line in card.inner_text().split("\n") if line.strip()]
                    
                    # 2. Извлечение локации (города)
                    location_list = []
                    if "place" in lines:
                        start_idx = lines.index("place") + 1
                        for i in range(start_idx, len(lines)):
                            current_line = lines[i]
                            # Ограничители блока локации: выход из цикла при встрече ключевых маркеров
                            if "Minimum qualifications" in current_line or "bar_chart" in current_line or current_line.startswith("Director"):
                                break
                            location_list.append(current_line)
                    
                    # Форматирование строки локации
                    location = " ".join(location_list).strip()
                    location = location.replace(" ;", ";").replace("; ", "; ")
                    if not location:
                        location = "Не указано"
                        
                    # 3. Извлечение минимальных требований (Minimum Qualifications)
                    qual_list = []
                    if "Minimum qualifications" in lines:
                        start_idx = lines.index("Minimum qualifications") + 1
                        for i in range(start_idx, len(lines)):
                            current_line = lines[i]
                            # Ограничители блока квалификаций
                            if "Preferred qualifications" in current_line or "About the job" in current_line:
                                break
                            qual_list.append(current_line)
                            
                    qualifications = "; ".join(qual_list).strip()
                    if not qualifications:
                        qualifications = "Не указано"
                    
                    # Добавление собранных данных в общий список
                    jobs_data.append({
                        "Профессия": title,
                        "Город / Локация": location,
                        "Минимальная квалификация": qualifications,
                        "Страница": current_page
                    })
                    
                    print(f"  [{index+1}] Собрано: {title} | Локация: {location}")
                    
                except Exception as card_error:
                    # Ошибка в отдельной карточке не должна прерывать сбор остальных данных
                    continue
            
            # Резервное сохранение данных каждые 5 страниц для предотвращения потери информации
            if current_page % 5 == 0:
                temp_df = pd.DataFrame(jobs_data)
                temp_df.to_csv("google_jobs_backup.csv", index=False, encoding="utf-8-sig")
                print(f"Создана резервная копия. Всего собрано на данный момент: {len(temp_df)}")
                
            current_page += 1
            time.sleep(1.5)  # Имитация задержки для снижения вероятности блокировки (CAPTCHA)
            
        browser.close()
        
        # Финальное сохранение результатов
        if jobs_data:
            final_df = pd.DataFrame(jobs_data)
            output_file = "google_final_database.csv"
            final_df.to_csv(output_file, index=False, encoding="utf-8-sig")
            
            print(f"\nСбор успешно завершен.")
            print(f"Финальный файл сохранен: '{output_file}'")
            print(f"Всего обработано страниц: {current_page - 1}")
            print(f"Итоговый размер датасета: {len(final_df)} вакансий")
        else:
            print("Сбор завершился без результатов.")

if __name__ == "__main__":
    scrape_entire_google_careers()
