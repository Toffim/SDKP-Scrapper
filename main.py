from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import re

from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

driver = webdriver.Chrome()
driver.get("https://sdkp.pjwstk.edu.pl/")

# Use this:
with open("password.txt", "r") as f:
    password = f.read().strip()
# Or just:
# password = "ILoveJava"

# Use this:
with open("studentIndex.txt", "r") as f:
    studentIndex = f.read().strip()
# Or just:
# studentIndex = "s10101"

# Login
driver.find_element(By.ID, "username").send_keys(studentIndex)
driver.find_element(By.ID, "password").send_keys(password)
driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

# Wait for login to complete
WebDriverWait(driver, 10).until(
    EC.url_contains("#studentPage")
)

# Now you can access protected pages
driver.get("https://sdkp.pjwstk.edu.pl/#studentPage")

task_scores = {}

# dropdown Rezultaty cwicznen, then go to selector of zadania and go through them, finding the points
try:
    # Find all collapsible sections
    collapsibles = driver.find_elements(By.CSS_SELECTOR, "[data-role='collapsible']")

    # Find the one containing "Rezultaty ćwiczeń"
    target_section = None
    for section in collapsibles:
        if "Rezultaty ćwiczeń" in section.text:
            target_section = section
            break

    if target_section:
        print("Found results section")

        # Check if collapsed (closed)
        if "ui-collapsible-content-collapsed" in target_section.get_attribute("class"):
            # Find the toggle button
            toggle = target_section.find_element(By.CSS_SELECTOR, ".ui-collapsible-heading-toggle")
            toggle.click()
            # Wait for animation to complete
            WebDriverWait(driver, 5).until(
                lambda d: "ui-collapsible-content-collapsed" not in target_section.get_attribute("class")
            )

        # Now find all tasks
        tasks = target_section.find_elements(By.TAG_NAME, "a")
        print(f"Found {len(tasks)} tasks")

        for task in tasks:
            task_name = task.text.strip()
            print(f"\nProcessing: {task_name}")

            # Click the task
            task.click()

            # Use Select class to interact with the dropdown
            task_dropdown = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "studentTasks"))
            )
            select = Select(task_dropdown)

            # Process all task options
            task_options = WebDriverWait(driver, 5).until(
                lambda d: [opt for opt in select.options if opt.text.strip()]
            )

            for option in task_options:
                task_name = option.text.strip()
                # Select the task from the dropdown
                select.select_by_visible_text(task_name)

                # Wait for results to load
                result_section = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.ID, "_SM_02_StudentTaskResults_Results"))
                )

                # Now extract the points from the page using regex
                try:
                    # Get the content containing points
                    result_section = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.ID, "_SM_02_StudentTaskResults_Results"))
                    )

                    # Extract points using regex
                    points_text = result_section.text

                    # Using regex to find the points value
                    match = re.search(r"Punkty uzyskane w wyniku testów:\s*(\d+)", points_text)
                    if match:
                        points = match.group(1)  # Extract the numeric value
                        # print(f"Points for {task_name}: {points}")
                        task_scores[task_name] = int(points)
                    else:
                        task_scores[task_name] = int(0)
                        # print(f"Points not found for {task_name}")

                except Exception as e:
                    print(f"Error extracting points for {task_name}: {e}")

            # Go back
            driver.back()
            time.sleep(1)

    else:
        print("Could not find results section")

except Exception as e:
    #print(f"Error occurred: {str(e)}")
    # Take screenshot for debugging
    driver.save_screenshot("error.png")
finally:
    driver.quit()


print("==== PUNKTY")
for task_name, score in task_scores.items():
    print(f"{task_name}: {score}")

best_scores = {}

for task_name, score in task_scores.items():
    # Wyciągnięcie "TPO-1", "TPO-2" itd. za pomocą regexa
    match = re.match(r"(TPO-\d+)", task_name)
    if match:
        base_task = match.group(1)  # Pobiera "TPO-1" albo "TPO-2"
        score = int(score)  # Konwersja wyniku na int
        if base_task not in best_scores or score > best_scores[base_task]:
            best_scores[base_task] = score

# Sumowanie najlepszych wyników
total_best_score = sum(best_scores.values())

print("\nNajwyższe wyniki dla każdego zadania:")
for base_task, best_score in best_scores.items():
    print(f"{base_task}: {best_score}")

print(f"\nSuma najlepszych wyników: {total_best_score}")

