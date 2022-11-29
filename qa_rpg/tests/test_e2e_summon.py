from selenium.webdriver.common.by import By
from selenium import webdriver


def test_create_question():
    """Players can create a question when they input every field."""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    selenium = webdriver.Chrome(options=options)

    live_server_url = "https://www.qarpg.tech/qa_rpg/"
    selenium.get(live_server_url)
    play_button = selenium.find_element(By.XPATH, '//button[text()="Play Now!"]')
    play_button.click()
    username = selenium.find_element(By.XPATH, '//input[@name="login"]')
    username.click()
    username.send_keys("demo")
    password = selenium.find_element(By.XPATH, '//input[@name="password"]')
    password.click()
    password.send_keys("12345")
    selenium.find_element(By.XPATH, '//button[text()="Login"]').click()

    selenium.find_element(By.XPATH, '//button[text()="summon"]').click()
    selenium.find_element(By.XPATH, '/html/body/form/div[2]/div/div/label').click()
    selenium.find_element(By.XPATH, '//button[text()="Choose"]').click()

    selenium.find_element(By.XPATH, '/html/body/form/div[2]/div/div[1]/label').click()
    for i in range(4):
        choice_input = selenium.find_element(By.XPATH, f'//input[@name="choice{i}"]')
        choice_input.click()
        choice_input.send_keys(f"{i + 1}")
    selenium.find_element(By.XPATH, '//button[text()="Summon: 50 coins"]').click()
    assert("/qa_rpg/index/" in selenium.current_url)
    summon_success_text = selenium.find_element(By.CLASS_NAME, "success")
    assert(summon_success_text.find_element(By.XPATH,
           '//*[text()[contains(., "Successfully summoned a new monster.")]]') is not None)


if __name__ == "__main__":
    test_create_question()

