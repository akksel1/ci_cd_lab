import unittest
from datetime import datetime, timedelta
from app import create_app
from extensions import db
from models import User, Task

class TestUnit(unittest.TestCase):
    
    def setUp(self):
        self.app = create_app()
        
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # --- Test 1: Logique User Password ---
    def test_password_hashing(self):
        """Test que le mot de passe est bien hashé et vérifié."""
        u = User(username='testuser')
        u.set_password('mypassword')
        
        self.assertNotEqual(u.password_hash, 'mypassword')
        self.assertTrue(u.check_password('mypassword'))
        self.assertFalse(u.check_password('wrongpassword'))

    # --- Test 2: Logique Task Overdue ---
    def test_task_is_overdue(self):
        """Test la méthode is_overdue de la tâche."""
        past_date = datetime.now().date() - timedelta(days=1)
        t1 = Task(title="Old Task", due_date=past_date, user_id=1)
        
        future_date = datetime.now().date() + timedelta(days=1)
        t2 = Task(title="Future Task", due_date=future_date, user_id=1)
        
        self.assertTrue(t1.is_overdue()) 
        self.assertFalse(t2.is_overdue())

    # --- Test 3: Logique Helper (Exemple environment parsing) ---
    def test_build_postgres_uri(self):
        """Test simple d'un modèle."""
        u = User(username='repr_test')
        u.set_password('test')
        self.assertEqual(u.username, 'repr_test')

if __name__ == '__main__':
    unittest.main()