from django.test import tag
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import tag
from selenium import webdriver
from selenium.webdriver.common.by import By
from django.contrib.auth.models import User
from qa_rpg.items_catalog import ItemCatalog

class SeleniumTestShop(StaticLiveServerTestCase):

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
        self.selenium.get(self.live_server_url)
        self.selenium.find_element(By.XPATH, '//button[text()="Play Now!"]').click()
        self.selenium.find_element(By.XPATH, "//input[@name='login']").click()
        self.selenium.find_element(By.XPATH, "//input[@name='login']").send_keys('demo')
        self.selenium.find_element(By.XPATH, "//input[@name='password']").click()
        self.selenium.find_element(By.XPATH, "//input[@name='password']").send_keys('12345')
        self.selenium.find_element(By.XPATH, '//button[text()="Login"]').click()
        self.selenium.find_element(By.XPATH, '//button[text()="shop"]').click()

    @tag('e2e')
    def test_shop(self):
        item_list = ItemCatalog()
        items = item_list.get_store_items()
        self.selenium.find_element(By.XPATH, '//label[@for="Dungeon Candy1"]').click()
        self.selenium.find_element(By.XPATH, '//button[text()="Buy"]').click()
        self.selenium.find_element(By.XPATH, '//button[text()="Back"]').click()
        self.assertEqual()
