"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase
from app import app, db
from models import User, Message

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ["DATABASE_URL"] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data


app.config["WTF_CSRF_ENABLED"] = False


class MessageViewFunctionTests(TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            self.user = User(username="testuser", email="test@test.com", password="password")
            db.session.add(self.user)
            db.session.commit()
            
            self.message = Message(text="Test message", user_id=self.user.id)
            db.session.add(self.message)
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_messages_add_authenticated(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = self.user.id
            
            response = c.post('/messages/new', data={'text': 'New test message'})
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.location.endswith(f"/users/{self.user.id}"))

    def test_messages_add_unauthenticated(self):
        response = self.client.post('/messages/new', data={'text': 'New test message'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.endswith("/"))

    def test_messages_show(self):
        response = self.client.get(f'/messages/{self.message.id}')
        self.assertEqual(response.status_code, 200)

    def test_messages_destroy_authenticated(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = self.user.id
            
            response = c.post(f'/messages/{self.message.id}/delete')
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.location.endswith(f"/users/{self.user.id}"))

    def test_messages_destroy_unauthenticated(self):
        response = self.client.post(f'/messages/{self.message.id}/delete')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.endswith("/"))

if __name__ == '__main__':
    TestCase.main()
