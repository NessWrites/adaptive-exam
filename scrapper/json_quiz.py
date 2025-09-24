import time
import json
import os
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException, StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# --- 1. SETUP AND UTILITY FUNCTIONS ---

def setup_driver():
    """Set up Chrome WebDriver with appropriate options"""
    try:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-extensions')
        # Optional: Run in headless mode (without opening a browser window)
        # chrome_options.add_argument('--headless')

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except Exception as e:
        print(f"Error setting up driver: {e}")
        return None

def login(driver, username, password):
    """Log in to the admin portal"""
    try:
        print("Logging in...")
        driver.get("https://aishikshya.admin.fuseclassroom.com/login")
        WebDriverWait(driver, 45).until(
            EC.presence_of_element_located((By.NAME, "username"))
        ).send_keys(username)
        driver.find_element(By.NAME, "password").send_keys(password)
        driver.find_element(By.TAG_NAME, "button").click()

        WebDriverWait(driver, 45).until(
            lambda d: "login" not in d.current_url.lower()
        )
        print("Login successful!")
        return True
    except Exception as e:
        print(f"Error during login: {e}")
        return False

def wait_for_page_load(driver, timeout=15):
    """Wait for page to be completely loaded"""
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )
        time.sleep(2) # Additional sleep for dynamic content
        return True
    except TimeoutException:
        print("  Warning: Page load timeout, continuing anyway...")
        return False

def navigate_to_next_page(driver, current_page, retries=3):
    """Navigate to the next page in a paginated list"""
    for attempt in range(retries):
        try:
            print(f"  Navigating to page {current_page + 1}...")
            wait_for_page_load(driver)

            # Find the 'Next Page' button, ensuring it's not disabled
            next_button_xpath = "//a[contains(text(), 'Next Page')]/.."
            parent_li = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, next_button_xpath))
            )

            if 'disabled' in (parent_li.get_attribute('class') or ''):
                print("  'Next Page' button is disabled. Reached the last page.")
                return False

            next_button = parent_li.find_element(By.TAG_NAME, 'a')
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", next_button)

            print("  Clicked next page button. Waiting for page to load...")
            time.sleep(10) # Wait for page content to refresh
            wait_for_page_load(driver)
            return True
        except (NoSuchElementException, TimeoutException):
            print("  Could not find 'Next Page' button. Reached the last page.")
            return False
        except Exception as e:
            print(f"  Error navigating to next page (Attempt {attempt + 1}): {e}")
            time.sleep(5)
    print("  Failed to navigate to the next page after multiple retries.")
    return False

# --- 2. QUIZ-SPECIFIC SCRAPING FUNCTIONS ---

def change_rows_per_page_quiz(driver, rows=50):
    """Change the number of quizzes displayed per page."""
    try:
        print(f"  Attempting to change quizzes per page to {rows}...")
        wait_for_page_load(driver)
        select_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//select[contains(@class, 'form-control')]"))
        )
        select = Select(select_element)
        select.select_by_value(str(rows))
        print(f"  Waiting 10 seconds for quiz list to reload...")
        time.sleep(10)
        wait_for_page_load(driver, timeout=15)
        return True
    except Exception as e:
        print(f"  Could not change rows per page (this is optional): {e}")
        return False

def get_quiz_links(driver):
    """Extract all quiz scoreboard links from the main quiz page."""
    try:
        print("Navigating to quizzes page...")
        driver.get("https://aishikshya.admin.fuseclassroom.com/quizzes?academicYearId=65d47ca75d5d1d2a9d6c6124&filterBy=all&showAll=Only%20mine&")
        wait_for_page_load(driver)
        change_rows_per_page_quiz(driver, 50)

        all_quizzes = []
        page_num = 1
        max_pages = 50  # Safety break

        while page_num <= max_pages:
            print(f"Extracting quiz links from page {page_num}...")
            wait_for_page_load(driver)
            # Ensure at least one listing is present before parsing
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "listing")))
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            quiz_listings = soup.find_all('div', class_='listing')

            if not quiz_listings and page_num > 1:
                print("No more quiz listings found.")
                break

            for quiz in quiz_listings:
                title_elem = quiz.find('span', class_='listing--title')
                scoreboard_link_elem = quiz.find('a', href=lambda href: href and 'scoreboard' in href)

                if title_elem and scoreboard_link_elem:
                    title = title_elem.text.strip()
                    relative_url = scoreboard_link_elem['href']
                    full_url = urljoin(driver.current_url, relative_url)
                    if not any(q['title'] == title for q in all_quizzes):
                        all_quizzes.append({'title': title, 'url': full_url})

            if not navigate_to_next_page(driver, page_num):
                break
            page_num += 1

        print(f"Found {len(all_quizzes)} unique quizzes in total.")
        return all_quizzes
    except Exception as e:
        print(f"An error occurred while getting quiz links: {e}")
        return []

def scrape_correct_answers_from_submission(driver, submission_url):
    """Scrape questions and their correct answers from a perfect-score submission."""
    try:
        print("    Scraping submission for correct answers...")
        driver.get(submission_url)
        WebDriverWait(driver, 45).until(
            EC.presence_of_element_located((By.CLASS_NAME, "question--card"))
        )
        wait_for_page_load(driver)
        time.sleep(1)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        questions_data = []

        for card in soup.find_all('div', class_='question--card'):
            question_text = "Question text not found"
            correct_answer_text = "Correct answer not found"
            
            question_elem = card.find('li', class_='question--text')
            if question_elem:
                question_text = re.sub(r'^\d+\.\s*', '', question_elem.text.strip())

            # ================================================================= #
            # ## MODIFIED LOGIC TO HANDLE MULTIPLE CORRECT ANSWERS ## #
            # Use find_all to capture all checked inputs (for both radio and checkboxes)
            all_checked_inputs = card.find_all('input', checked=True)
            correct_answers_list = []
            
            if all_checked_inputs:
                for checked_input in all_checked_inputs:
                    answer_span = checked_input.find_next_sibling('span')
                    if answer_span:
                        correct_answers_list.append(answer_span.text.strip())
            
            if correct_answers_list:
                # Join multiple answers with a clear separator
                correct_answer_text = '; '.join(correct_answers_list)
            # ================================================================= #
            
            questions_data.append({
                'question': question_text,
                'correct_answer': correct_answer_text
            })

        print(f"    Extracted {len(questions_data)} questions and answers.")
        return questions_data
    except Exception as e:
        print(f"    Error scraping submission page {submission_url}: {e}")
        return []

def scrape_quiz_and_find_submission(driver, quiz_url, quiz_title):
    """Finds a perfect score on the scoreboard and scrapes its submission."""
    try:
        print(f"  Processing quiz: {quiz_title}")
        driver.get(quiz_url)
        
        print("    Waiting for scoreboard data to load...")
        scoreboard_row_selector = "table.table tbody tr"
        WebDriverWait(driver, 45).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, scoreboard_row_selector))
        )
        wait_for_page_load(driver)
        print("    Scoreboard loaded.")

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        tbody = soup.find('tbody')
        if not tbody:
            print("    No data in scoreboard table. Skipping.")
            return None

        for row in tbody.find_all('tr'):
            tds = row.find_all('td')
            if len(tds) < 7: continue

            score_text = tds[1].text.strip()
            match = re.match(r'(\d+)/(\d+)', score_text)
            if match:
                score, total = int(match.group(1)), int(match.group(2))
                if score == total and total > 0:
                    print(f"    Found a perfect score submission: {score}/{total}")
                    submission_link = tds[6].find('a', href=True)
                    if submission_link:
                        full_url = urljoin(driver.current_url, submission_link['href'])
                        return scrape_correct_answers_from_submission(driver, full_url)
        
        print(f"    Could not find a perfect score for '{quiz_title}'. Skipping.")
        return None
    except Exception as e:
        print(f"  An error occurred processing quiz '{quiz_title}': {e}")
        return None

# --- 3. MAIN EXECUTION ---

def main():
    """Main execution function to orchestrate the quiz scraping."""
    driver = setup_driver()
    if not driver:
        return

    output_dir = "quiz_answer"
    os.makedirs(output_dir, exist_ok=True)
    all_quiz_data = {}

    try:
        if not login(driver, "instructor1@fuse.ai", "@Fu53nepal"):
            return

        quizzes = get_quiz_links(driver)
        if not quizzes:
            print("No quizzes found. Exiting.")
            return

        print(f"\nFound {len(quizzes)} quizzes to process.")

        for i, quiz in enumerate(quizzes, 1):
            print(f"\n{'='*60}")
            print(f"Processing quiz {i}/{len(quizzes)}: {quiz['title']}")
            print(f"{'='*60}")

            quiz_results = scrape_quiz_and_find_submission(driver, quiz['url'], quiz['title'])
            if quiz_results:
                all_quiz_data[quiz['title']] = quiz_results
                print(f"✓ Successfully processed: {quiz['title']}")
            else:
                print(f"✗ Failed to process or no perfect score found for: {quiz['title']}")
            
            if i < len(quizzes):
                time.sleep(3)

        if all_quiz_data:
            filename = os.path.join(output_dir, "all_quiz_answers.json")
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(all_quiz_data, f, ensure_ascii=False, indent=2)
            print(f"\n{'='*60}")
            print(f"All quiz data saved to {filename}")
            print(f"Successfully scraped data for {len(all_quiz_data)} out of {len(quizzes)} quizzes.")
        else:
            print("\nNo data was collected from any quizzes.")

    except Exception as e:
        print(f"An unexpected error occurred in main: {e}")
    finally:
        print("Closing browser...")
        driver.quit()

if __name__ == "__main__":
    main()