from django.test import TestCase

from catalog.models import Author, Category, EduMaterial


class AuthorModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Author.objects.create(user=None, first_name="Somebody", last_name="Oncetoldme", info="Somebody info")

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
