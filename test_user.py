from unittest import TestCase

from app import app
from models import db, User
from sqlalchemy import exc

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///mealtest'
app.config['SQLALCHEMY_ECHO'] = False

class UserTestCase(TestCase):
    """Tests for views for Users."""

    def setUp(self):
        """Make demo data."""

        db.drop_all()
        db.create_all()


        user = User.register(
            username="user",
            password="hashed_pass",
            email="test@test.com",
            first_name="name",
            last_name="again",
            )
        user.id = 1
        user_id = user.id

        db.session.add(user)
        db.session.commit()

        self.user = User.query.get(user_id)

    def tearDown(self):
        """Clean up fouled transactions."""

        db.session.rollback()
        db.drop_all()

    def test_user_register(self):
        '''test form can get values'''
        u = User(
            username='test',
            password='HASHED_PASS',
            email='test@test.com',
            first_name='testf',
            last_name='testl',
            
        )
        u.id = 2
        u_id = u.id
        db.session.add(u)
        db.session.commit()
        user = User.query.get(u_id)
        self.assertEqual(user.first_name, 'testf')
        self.assertEqual(user.username,'test')
        self.assertEqual(user.email,'test@test.com')

    def test_valid_register(self):
        '''is the registration a valid one'''
        valid = User.register(
                'test',
                'pass',
                'test@test.com',
                'testf',
                'testl',
                
            )
        valid.id = 21
        valid_id = valid.id
        
        db.session.commit()
        valid = User.query.get(valid_id)
        
        self.assertEquals(valid.username, "test")
        self.assertEquals(valid.email, "test@test.com")
        self.assertEquals(valid.first_name, "testf")
        self.assertEquals(valid.last_name, "testl")
        self.assertNotEquals(valid.password, "pass")

    def test_invalid_register(self):
        '''email with no @ or .com ending'''
        invalid = User.register(
                'test',
                'pass',
                'email',
                'testf',
                'testl',
                
            )
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()