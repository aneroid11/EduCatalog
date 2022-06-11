from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files import File

from catalog.models import Author, Category, EduMaterial


class AuthorModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create_user("somename", email="someemail@example.com", password="12345687")
        Author.objects.create(user=User.objects.get(username__exact="somename"),
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
        # parent category
        User.objects.create(username="somename", email="someemail@example.com", password="12345687")
        User.objects.create(username="somename2", email="someemail2@example.com", password="12345687")
        Category.objects.create(name="parent",
                                info="some parent category",
                                parent_category=None)
        parent_category = Category.objects.get(id=1)
        parent_category.users_subscribed.add(User.objects.get(username__exact="somename"))
        parent_category.save()

        # child category
        Category.objects.create(name="child",
                                info="some child category",
                                parent_category=parent_category)
        child_category = Category.objects.get(id=2)
        child_category.users_subscribed.add(User.objects.get(username__exact="somename2"))
        child_category.save()

    def test_str(self):
        category = Category.objects.get(id=2)
        self.assertEqual(str(category), category.name)

    def test_get_absolute_url(self):
        category = Category.objects.get(id=1)
        self.assertEqual(category.get_absolute_url(),
                         "/catalog/category/1")

    def test_get_absolute_url_for_subscribe(self):
        category = Category.objects.get(id=1)
        self.assertEqual(category.get_absolute_url_for_subscribe(),
                         "/catalog/category/1/subscribe")

    def test_labels(self):
        category = Category.objects.get(id=1)
        self.assertEqual(category._meta.get_field('name').max_length, 100)
        self.assertEqual(category._meta.get_field('info').max_length, 1000)

    def test_parent_category(self):
        category = Category.objects.get(id=2)
        parent_category = Category.objects.get(id=1)
        self.assertEqual(parent_category, category.parent_category)

    def test_users_subscribed(self):
        parent_category = Category.objects.get(id=1)
        child_category = Category.objects.get(id=2)

        users_parent_category = parent_category.users_subscribed
        self.assertEqual(users_parent_category.count(), 1)
        self.assertEqual(users_parent_category.get_queryset()[0], User.objects.get(username__exact="somename"))

        users_child_category = child_category.users_subscribed
        self.assertEqual(users_child_category.count(), 1)
        self.assertEqual(users_child_category.get_queryset()[0], User.objects.get(username__exact="somename2"))


class EduMaterialModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # author
        User.objects.create_user("someauthor", email="someauthor@example.com", password="12345687")
        Author.objects.create(user=User.objects.get(username__exact="someauthor"),
                              first_name="Someauthor",
                              last_name="Oncetoldme",
                              info="Someauthor info")

        # parent category
        User.objects.create(username="somename", email="someemail@example.com", password="12345687")
        User.objects.create(username="somename2", email="someemail2@example.com", password="12345687")
        Category.objects.create(name="parent",
                                info="some parent category",
                                parent_category=None)
        parent_category = Category.objects.get(name__exact="parent")
        parent_category.users_subscribed.add(User.objects.get(username__exact="somename"))
        parent_category.save()

        # child category
        Category.objects.create(name="child",
                                info="some child category",
                                parent_category=parent_category)
        child_category = Category.objects.get(name="child")
        child_category.users_subscribed.add(User.objects.get(username__exact="somename2"))
        child_category.save()

        EduMaterial.objects.create(title="Material 1",
                                   summary="Some material 1 in parent category",
                                   author=Author.objects.get(first_name="Someauthor"),
                                   access_type='p',
                                   pdf_file=File(open("pdfmaterials/some_pdf.pdf", 'rb')))
        edu_material = EduMaterial.objects.get(id=1)
        edu_material.category.add(child_category)

    def test_labels(self):
        material = EduMaterial.objects.get(id=1)
        self.assertEqual(material._meta.get_field('title').max_length, 200)
        self.assertEqual(material._meta.get_field('summary').max_length, 1000)
        self.assertEqual(material._meta.get_field('access_type').max_length, 1)

    def test_author(self):
        material = EduMaterial.objects.get(id=1)
        author = Author.objects.get(first_name='Someauthor')
        self.assertEqual(material.author, author)
