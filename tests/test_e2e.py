import unittest
import threading
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from app import create_app
from extensions import db
from models import User

class TestE2E(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Configuration globale : lancée une seule fois avant tous les tests"""
        cls.app = create_app({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///e2e.db',
            'WTF_CSRF_ENABLED': False
        })
        
        with cls.app.app_context():
            db.create_all()
            if not User.query.filter_by(username='e2e_user').first():
                u = User(username='e2e_user')
                u.set_password('secure123')
                db.session.add(u)
                db.session.commit()

        cls.server_thread = threading.Thread(target=cls.app.run, kwargs={'port': 5002, 'use_reloader': False})
        cls.server_thread.daemon = True
        cls.server_thread.start()
        
        time.sleep(1)

        options = webdriver.ChromeOptions()
        options.add_argument("--headless") 
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        cls.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        cls.driver.implicitly_wait(2) 

    @classmethod
    def tearDownClass(cls):
        """Nettoyage après les tests"""
        cls.driver.quit()
        # Supprimer la BDD temporaire
        if os.path.exists('e2e.db'):
            os.remove('e2e.db')

    def test_1_login(self):
        driver = self.driver
        driver.get('http://localhost:5002/login')
        
        driver.find_element(By.NAME, 'username').send_keys('e2e_user')
        driver.find_element(By.NAME, 'password').send_keys('secure123')
        
        submit_btn = driver.find_element(By.TAG_NAME, 'button')
        submit_btn.click()
        
        self.assertIn('Your Tasks', driver.page_source)
        self.assertIn('Logged in as e2e_user', driver.page_source)
        
    def test_2_create_task(self):
        driver = self.driver
        
        driver.get('http://localhost:5002/tasks/new')
        
        driver.find_element(By.NAME, 'title').send_keys('Selenium Task')
        driver.find_element(By.NAME, 'description').send_keys('Automated by robot')
        
        driver.find_element(By.TAG_NAME, 'button').click()
        
        self.assertIn('Selenium Task', driver.page_source)

    def test_3_toggle_task(self):
        driver = self.driver
        driver.get('http://localhost:5002/')
        
        self.assertIn('Open', driver.page_source)
        
        buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Complete')]")
        if buttons:
            buttons[0].click()
            
            self.assertIn('Done', driver.page_source)
            self.assertIn('Reopen', driver.page_source)
        else:
            self.fail("Bouton Complete introuvable")

if __name__ == '__main__':
    unittest.main()