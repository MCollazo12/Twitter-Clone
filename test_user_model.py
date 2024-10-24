"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py

import os
from unittest import TestCase
from models import db, User, Message, Follows
from sqlalchemy import exc

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ["DATABASE_URL"] = "postgresql:///warbler-test"


# Now we can import app
from app import app

# Configure the app for testing
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
app.config["TESTING"] = True

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data


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
        self.client = app.test_client()

        with app.app_context():
            User.query.delete()
            Message.query.delete()
            Follows.query.delete()
            db.session.commit()

            # Create a sample test user
            self.user = User.signup(
                username="testuser",
                email="test@test.com",
                password="HASHED_PASSWORD",
                image_url=None,
            )
            db.session.add(self.user)
            db.session.commit()

    def tearDown(self):
        """Clean up any fouled transaction."""
        with app.app_context():
            db.session.rollback()

    ############################## USER SIGNUP TESTS ################################
    def test_user_creation(self):
        """Test whether a new user is created successfully given valid credentials."""
        with app.app_context():
            u = User.signup(
                username="testuser2",
                email="test2@test.com",
                password="password",
                image_url=None,
            )
            db.session.commit()

            self.assertIsNotNone(u.id)
            self.assertEqual(u.username, "testuser2")
            self.assertEqual(u.email, "test2@test.com")
            self.assertTrue(u.password.startswith("$2b$"))

    def test_invalid_username_signup(self):
        """Test that signing up with an invalid (None) username raises an IntegrityError."""
        with app.app_context():
            with self.assertRaises(exc.IntegrityError):
                u = User.signup(
                    username=None,
                    email="test@test.com",
                    password="password",
                    image_url=None,
                )
                db.session.commit()

    def test_invalid_email_signup(self):
        """Test that signing up with an invalid (None) email raises an IntegrityError."""
        with app.app_context():
            with self.assertRaises(exc.IntegrityError):
                u = User.signup(
                    username="testuser3",
                    email=None,
                    password="password",
                    image_url=None,
                )
                db.session.commit()

    def test_invalid_password_signup(self):
        with self.assertRaises(ValueError) as context:
            User.signup(
                username="testtest",
                email="email@email.com",
                password="",
                image_url=None
            )

        with self.assertRaises(ValueError) as context:
            User.signup(
                username="testtest",
                email="email@email.com",
                password=None,
                image_url=None,
            )

    ############################## USER AUTHENTICATION TESTS ################################
    def test_authenticate_valid_user(self):
        """Test authenticating a valid user."""
        with app.app_context():
            # Attempt to authenticate with valid credentials
            authenticated_user = User.authenticate("testuser", "HASHED_PASSWORD")
            # Check if the authenticated user is not None
            self.assertIsNotNone(authenticated_user)
            # Check if the username of the authenticated user is correct
            self.assertEqual(authenticated_user.username, "testuser")

    def test_authenticate_invalid_username(self):
        """Test authenticating with an invalid username."""
        with app.app_context():
            # Attempt to authenticate with an invalid username
            authenticated_user = User.authenticate("wrongusername", "HASHED_PASSWORD")

            # Check if the authenticated user is None
            self.assertFalse(authenticated_user)

    def test_authenticate_invalid_password(self):
        """Test authenticating with an invalid password."""
        with app.app_context():
            # Attempt to authenticate with an invalid password
            authenticated_user = User.authenticate("testuser", "wrongpassword")

            # Check if the authenticated user is None
            self.assertFalse(authenticated_user)
