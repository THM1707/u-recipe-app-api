from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models
from unittest.mock import patch


def sample_user(email='example@gmail.com', password='password') -> models.User:
    """Create a sample user"""
    return get_user_model().objects.create_user(email=email, password=password)


class ModelTest(TestCase):
    def test_create_user_with_email(self):
        """Check if new user created successfully"""
        email = 'example@gmail.com'
        password = 'password'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """ Test if email for new user is normalized """
        email = 'example@gmail.COM'
        password = 'password'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """ Test create user with invalid email error """
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'password')

    def test_create_new_superuser(self):
        """ Test creating new superuser """
        user = get_user_model().objects.create_superuser('super@gmail.com', 'password')

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """Test the tag string representation"""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Vegan'
        )

        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        """Test the ingredient str representative"""
        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name='Cucumber'
        )

        self.assertEqual(str(ingredient), ingredient.name)

    def test_recipe_str(self):
        """Test the recipe string representation"""
        recipe = models.Recipe.objects.create(
            user=sample_user(),
            title='Steak and mushroom sauce',
            time_minutes=5,
            price=5.0
        )

        self.assertEqual(str(recipe), recipe.title)

    @patch('uuid.uuid4')
    def test_recipe_file_name_uuid(self, mock_uuid):
        """Test that image is saved in the correct location"""
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None, 'my_id.jpeg')

        exp_path = f'uploads/recipe/{uuid}.jpeg'
        self.assertEqual(file_path, exp_path)
