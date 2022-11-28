from selenium import webdriver
from selenium.webdriver.common.by import By


def e2e_upgrade():
    selenium = webdriver.Chrome()
    selenium.get("https://www.qarpg.tech/")
    selenium.find_element(By.XPATH, '//button[text()="Play Now!"]').click()
    selenium.find_element(By.XPATH, "//input[@name='login']").click()
    selenium.find_element(By.XPATH, "//input[@name='login']").send_keys('demo')
    selenium.find_element(By.XPATH, "//input[@name='password']").click()
    selenium.find_element(By.XPATH, "//input[@name='password']").send_keys('12345')
    selenium.find_element(By.XPATH, '//button[text()="Login"]').click()
    selenium.find_element(By.XPATH, '//button[text()="profile"]').click()
    selenium.find_element(By.XPATH, '//button[text()="Items Inventory"]').click()
    assert ("/qa_rpg/profile/" in selenium.current_url)
    selenium.find_element(By.XPATH, '//button[text()="Templates Inventory"]').click()
    assert ("/qa_rpg/profile/select_template" in selenium.current_url)
    selenium.find_element(By.XPATH, '//button[text()="Back"]').click()
    assert ("/qa_rpg/index/" in selenium.current_url)
    selenium.find_element(By.XPATH, '//button[text()="profile"]').click()
    selenium.find_element(By.XPATH, '//button[text()="Upgrade"]').click()
    assert ("/qa_rpg/profile/upgrade/" in selenium.current_url)
    selenium.find_element(By.XPATH, "//button[@name='max_hp']").click()
    text = selenium.find_element(By.CLASS_NAME, "error")
    assert (text is not None)
    selenium.find_element(By.XPATH, "//button[@name='max_currency']").click()
    text = selenium.find_element(By.CLASS_NAME, "error")
    assert (text is not None)
    selenium.find_element(By.XPATH, "//button[@name='rate_currency']").click()
    text = selenium.find_element(By.CLASS_NAME, "error")
    assert (text is not None)
    selenium.find_element(By.XPATH, "//button[@name='awake']").click()
    text = selenium.find_element(By.CLASS_NAME, "error")
    assert (text is not None)
    selenium.find_element(By.XPATH, '//button[text()="Back"]').click()
    assert ("/qa_rpg/profile/" in selenium.current_url)
    selenium.find_element(By.XPATH, '//button[text()="Back"]').click()
    assert ("/qa_rpg/index/" in selenium.current_url)


if __name__ == '__main__':
    e2e_upgrade()