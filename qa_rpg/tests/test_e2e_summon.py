from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth.models import User
from django.test import tag
from qa_rpg.models import Player
from selenium.webdriver.common.by import By
from selenium import webdriver


class TestSummon(StaticLiveServerTestCase):

    @classmethod
    def setUp(cls) -> None:
        """Setup for testing creating questions feature."""
        super().setUpClass()
        cls.selenium = webdriver.Chrome()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    @tag('e2e')
    def test_create_question(self):
        """Players can create a question when they input every field."""
        self.demo = User.objects.create_user(username="demo", email="demo@gmail.com")
        self.demo.set_password("12345")
        self.demo.save()
        self.demo_player = Player.objects.create(user=self.demo)
        self.demo_player.currency = 50
        self.demo_player.save()
        self.selenium.get(self.live_server_url)
        play_button = self.selenium.find_element(By.XPATH, '//button[text()="Play Now!"]')
        play_button.click()
        username = self.selenium.find_element(By.XPATH, '//input[@name="login"]')
        username.click()
        username.send_keys("demo")
        password = self.selenium.find_element(By.XPATH, '//input[@name="password"]')
        password.click()
        password.send_keys("12345")
        self.selenium.find_element(By.XPATH, '//button[text()="Login"]').click()

        self.selenium.find_element(By.XPATH, '//button[text()="summon"]').click()
        self.selenium.find_element(By.XPATH, '/html/body/form/div[2]/div/div/label').click()
        self.selenium.find_element(By.XPATH, '//button[text()="Choose"]').click()

        self.selenium.find_element(By.XPATH, '/html/body/form/div[2]/div/div[1]/label').click()
        for i in range(4):
            choice_input = self.selenium.find_element(By.XPATH, f'//input[@name="choice{i}"]')
            choice_input.click()
            choice_input.send_keys(f"{i + 1}")
