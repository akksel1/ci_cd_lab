import unittest
from app import create_app
from extensions import db
from models import User, Task

class TestIntegration(unittest.TestCase):
    
    def setUp(self):
        self.app = create_app({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'WTF_CSRF_ENABLED': False
        })
        
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login(self, username, password):
        return self.client.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    # --- Test 1: Flux Inscription + Login [cite: 182] ---
    def test_register_and_login(self):
        response = self.client.post('/register', data=dict(
            username='newuser',
            password='securepassword',
            confirm='securepassword'  
        ), follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Registration successful', response.data)

        response = self.login('newuser', 'securepassword')
        self.assertIn(b'Logged in successfully', response.data) 

    def test_create_task(self):
        self.client.post('/register', data={'username': 'taskuser', 'password': 'pw', 'confirm': 'pw'}, follow_redirects=True)
        self.login('taskuser', 'pw')

        response = self.client.post('/tasks/new', data=dict(
            title='Integration Task',
            description='Testing creation',
            due_date='2025-12-31'
        ), follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Task created', response.data)
        
        task = Task.query.filter_by(title='Integration Task').first()
        self.assertIsNotNone(task)
        self.assertEqual(task.description, 'Testing creation')

    def test_toggle_task(self):
        # Setup: User + Task
        u = User(username='edituser')
        u.set_password('pw')
        db.session.add(u)
        db.session.commit()
        
        t = Task(title="To Toggle", user_id=u.id, is_completed=False)
        db.session.add(t)
        db.session.commit()

        self.login('edituser', 'pw')

        response = self.client.post(f'/tasks/{t.id}/toggle', follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Task status updated', response.data)
        
        updated_task = db.session.get(Task, t.id)
        self.assertTrue(updated_task.is_completed)

if __name__ == '__main__':
    unittest.main()