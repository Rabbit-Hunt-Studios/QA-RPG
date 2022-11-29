from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def test_enter_dungeon():
    """Test e2e about the dungeon system."""

    ### Headless selenium
    # chrome_options = Options()
    # chrome_options.add_argument("--headless")
    # selenium = webdriver.Chrome(options=chrome_options)

    ### Default selenium
    selenium = webdriver.Chrome()
    selenium.get("https://www.qarpg.tech/")
    selenium.find_element(By.XPATH, '//button[text()="Play Now!"]').click()
    selenium.find_element(By.XPATH, "//input[@name='login']").click()
    selenium.find_element(By.XPATH, "//input[@name='login']").send_keys('demo')
    selenium.find_element(By.XPATH, "//input[@name='password']").click()
    selenium.find_element(By.XPATH, "//input[@name='password']").send_keys('12345')
    selenium.find_element(By.XPATH, '//button[text()="Login"]').click()

    selenium.find_element(By.XPATH, '//button[text()="dungeon"]').click()
    assert ("/qa_rpg/select/" in selenium.current_url)
    selenium.find_element(By.XPATH, '/html/body/form/div[1]/div[1]/div/div[1]/label').click()
    selenium.find_element(By.XPATH, '/html/body/form/div[2]/div/div/input').click()
    selenium.find_element(By.XPATH, '//button[text()="Select"]').click()
    selenium.find_element(By.XPATH, '/html/body/form/div[1]/div[2]/div/div/label').click()
    selenium.find_element(By.XPATH, '/html/body/form/div[2]/div/div/input').click()
    selenium.find_element(By.XPATH, '//button[text()="Select"]').click()
    selenium.find_element(By.XPATH, '//button[text()="Dungeon"]').click()

    assert ("/qa_rpg/dungeon/" in selenium.current_url)
    selenium.find_element(By.XPATH, '//button[text()="Exit"]').click()

if __name__ == '__main__':
    test_enter_dungeon()