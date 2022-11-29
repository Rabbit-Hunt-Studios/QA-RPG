from selenium import webdriver
from selenium.webdriver.common.by import By


def test_enter_dungeon(self):
    """Test e2e about the dungeon system."""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")

    selenium = webdriver.Chrome(options=options)
    selenium.get("https://www.qarpg.tech/")
    selenium.find_element(By.XPATH, '//button[text()="Play Now!"]').click()
    selenium.find_element(By.XPATH, "//input[@name='login']").click()
    selenium.find_element(By.XPATH, "//input[@name='login']").send_keys('demo')
    selenium.find_element(By.XPATH, "//input[@name='password']").click()
    selenium.find_element(By.XPATH, "//input[@name='password']").send_keys('12345')
    selenium.find_element(By.XPATH, '//button[text()="Login"]').click()

    selenium.find_element(By.XPATH, '//button[text()="dungeon"]').click()
    selenium.find_element(By.XPATH, '/html/body/form/div[1]/div[1]/div/div[1]/label').click()
    selenium.find_element(By.XPATH, '/html/body/form/div[2]/div/div/input').click()
    selenium.find_element(By.XPATH, '/html/body/form/div[2]/div/div/input').send_keys('3')
    selenium.find_element(By.XPATH, '//button[text()="select"]').click()
    selenium.find_element(By.XPATH, '/html/body/form/div[1]/div[2]/div/div/label').click()
    selenium.find_element(By.XPATH, '/html/body/form/div[2]/div/div/input').click()
    selenium.find_element(By.XPATH, '/html/body/form/div[2]/div/div/input').send_keys('1')
    selenium.find_element(By.XPATH, '//button[text()="select"]').click()
    selenium.find_element(By.XPATH, '//button[text()="Dungeon"]').click()

    selenium.find_element(By.XPATH, '//button[text()="Walk"]').click()
    selenium.find_element(By.XPATH, '//button[text()="Walk"]').click()
    selenium.find_element(By.XPATH, '//button[text()="Exit"]').click()