from django.test import tag
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver
from django.contrib.auth.models import User


class MySeleniumTests(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = WebDriver()
        cls.selenium.implicitly_wait(10)

        
    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    @tag('e2e')
    def setUp(self) -> None:
        self.user = User.objects.create_user(username = "demo")
        self.user.set_password("12345")
        self.user.save()
        self.selenium.get(self.live_server_url)
        self.selenium.find_element(By.XPATH, '//button[text()="Play Now!"]').click()
        self.selenium.find_element(By.XPATH, '//input[@name="login"]').click()
        self.selenium.find_element(By.XPATH, '//input[@name="login"]').send_keys("demo")
        self.selenium.find_element(By.XPATH, '//input[@name="password"]').click()
        self.selenium.find_element(By.XPATH, '//input[@name="password"]').send_keys("12345")
        self.selenium.find_element(By.XPATH, '//button[text()="Login"]').click()
        self.selenium.find_element(By.XPATH, '//button[text()="dungeon"]').click()

    @tag('e2e')
    def test_select_item(self):
        self.assertIn("/qa_rpg/select/", self.selenium.current_url)
        self.selenium.find_element(By.XPATH, '/html/body/form/div[1]/div[1]/div/div[1]/label').click()
        self.selenium.find_element(By.XPATH, '/html/body/form/div[2]/div/div/input').click()
        self.selenium.find_element(By.XPATH, '/html/body/form/div[2]/div/div/input').send_keys("3")
        self.selenium.find_element(By.XPATH, '//button[text()="Select"]').click()
        text = self.selenium.find_element(By.CLASS_NAME, "error")
        self.assertTrue(text is not None)
        self.assertIn("/qa_rpg/select/", self.selenium.current_url)

    @tag('e2e')
    def test_enter_dungeon(self):
        self.selenium.find_element(By.XPATH, '//button[text()="Dungeon"]').click()
        self.assertIn("/qa_rpg/dungeon/", self.selenium.current_url)   
        self.selenium.find_element(By.XPATH, '//button[text()="Walk"]').click()
        self.assertIn("/qa_rpg/dungeon/", self.selenium.current_url)  
        
        
  