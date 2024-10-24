"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_message_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows, Likes

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ["DATABASE_URL"] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    @classmethod
    def setUpClass(cls):
        """Set up the database tables once for all tests."""
        with app.app_context():
            db.create_all()

    @classmethod
    def tearDownClass(cls):
        """Drop the database tables once all tests are done."""
        with app.app_context():
            db.drop_all()

    def setUp(self):
        """Create test client, add sample data."""
        with app.app_context():
            self.uid = 94566
            u = User.signup("testing", "testing@test.com", "password", None)
            u.id = self.uid
            db.session.commit()

            self.u = User.query.get(self.uid)

            self.client = app.test_client()

    def tearDown(self):
        with app.app_context():
            res = super().tearDown()
            db.session.rollback()
            return res

    def test_message_model(self):
        message = Message(text="Test message", user_id=self.user.id)
        db.session.add(message)
        db.session.commit()

        self.assertEqual(Message.query.count(), 1)
        self.assertEqual(Message.query.first().text, "Test message")
        self.assertEqual(Message.query.first().user_id, self.user.id)

    def test_message_user_relationship(self):
        message = Message(text="Test message", user_id=self.user.id)
        db.session.add(message)
        db.session.commit()

        self.assertEqual(message.user, self.user)
        self.assertIn(message, self.user.messages)


if __name__ == "__main__":
    unittest.main()
