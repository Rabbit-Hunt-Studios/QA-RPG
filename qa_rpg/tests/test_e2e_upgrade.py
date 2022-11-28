import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from django.contrib.auth.models import User


class MySeleniumTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = webdriver.Chrome()
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def setUp(self):
        self.user = User.objects.create_user(username="demo")
        self.user.set_password("12345")
        self.user.save()
        self.selenium.get("https://www.qarpg.tech/")
        self.selenium.find_element(By.XPATH, '//button[text()="Play Now!"]').click()
        self.selenium.find_element(By.XPATH, "//input[@name='login']").click()
        self.selenium.find_element(By.XPATH, "//input[@name='login']").send_keys('demo')
        self.selenium.find_element(By.XPATH, "//input[@name='password']").click()
        self.selenium.find_element(By.XPATH, "//input[@name='password']").send_keys('12345')
        self.selenium.find_element(By.XPATH, '//button[text()="Login"]').click()
        self.selenium.find_element(By.XPATH, '//button[text()="profile"]').click()

    def test_profile(self):
        self.selenium.find_element(By.XPATH, '//button[text()="Items Inventory"]').click()
        self.assertIn("/qa_rpg/profile/", self.selenium.current_url)
        self.selenium.find_element(By.XPATH, '//button[text()="Templates Inventory"]').click()
        self.assertIn("/qa_rpg/profile/select_template", self.selenium.current_url)
        self.selenium.find_element(By.XPATH, '//button[text()="Back"]').click()
        self.assertIn("/qa_rpg/index/", self.selenium.current_url)

    def test_upgrade(self):
        self.selenium.find_element(By.XPATH, '//button[text()="Upgrade"]').click()
        self.assertIn("/qa_rpg/profile/upgrade/", self.selenium.current_url)
        self.selenium.find_element(By.XPATH, "//button[@name='max_hp']").click()
        text = self.selenium.find_element(By.CLASS_NAME, "error")
        self.assertTrue(text is not None)
        self.selenium.find_element(By.XPATH, "//button[@name='max_currency']").click()
        text = self.selenium.find_element(By.CLASS_NAME, "error")
        self.assertTrue(text is not None)
        self.selenium.find_element(By.XPATH, "//button[@name='rate_currency']").click()
        text = self.selenium.find_element(By.CLASS_NAME, "error")
        self.assertTrue(text is not None)
        self.selenium.find_element(By.XPATH, "//button[@name='awake']").click()
        text = self.selenium.find_element(By.CLASS_NAME, "error")
        self.assertTrue(text is not None)
        self.selenium.find_element(By.XPATH, '//button[text()="Back"]').click()
        self.assertIn("/qa_rpg/profile/", self.selenium.current_url)
        self.selenium.find_element(By.XPATH, '//button[text()="Back"]').click()
        self.assertIn("/qa_rpg/index/", self.selenium.current_url)
