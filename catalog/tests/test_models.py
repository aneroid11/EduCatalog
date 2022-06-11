from django.test import TestCase

from catalog.models import Author, Category, EduMaterial
from django.contrib.auth.models import User


class AuthorModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create_user("somename", email="someemail@example.com", password="12345687")
        Author.objects.create(user=User.objects.get(id=1),
                              first_name="Somebody",
                              last_name="Oncetoldme",
                              info="Somebody info")

    def test_author_user(self):
        author = Author.objects.get(id=1)
        self.assertEqual(author.user, User.objects.get(id=1))

    def test_labels_max_length(self):
        author = Author.objects.get(id=1)
        self.assertEqual(author._meta.get_field('first_name').max_length, 100)
        self.assertEqual(author._meta.get_field('last_name').max_length, 100)
        self.assertEqual(author._meta.get_field('info').max_length, 1000)

    def test_get_absolute_url(self):
        author = Author.objects.get(id=1)
        self.assertEqual(author.get_absolute_url(), "/catalog/author/1")

    def test_str(self):
        author = Author.objects.get(id=1)
        self.assertEqual(str(author), f"{author.first_name} {author.last_name}")


class CategoryModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        
