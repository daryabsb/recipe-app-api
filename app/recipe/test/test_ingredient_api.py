from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient
from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')


class PublicIngredientAPITest(TestCase):
    # Test the publicly available ingredient api

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        # Test that login is required always
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientAPITest(TestCase):
    # Test the private ingredients api

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'root@root.com',
            'Welcome1234'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredient_list(self):
        # Test retrieving ingredients list
        Ingredient.objects.create(user=self.user, name='Kale')
        Ingredient.objects.create(user=self.user, name='Salt')

        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredient_limited_to_user(self):
        # Test that only ingredient for the authenticated user returned
        user2 = get_user_model().objects.create_user(
            'zane@darya.comDarya@2018',
            'Welcome2431'
        )
        Ingredient.objects.create(user=user2, name='Vineger')

        ingredient = Ingredient.objects.create(user=self.user, name='Tumeric')

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)
