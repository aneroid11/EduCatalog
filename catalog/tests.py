import logging

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files import File
from django.shortcuts import reverse

from . import models
from . import forms
from . import views


class AuthorModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create_user("somename", email="someemail@example.com", password="12345687")
        models.Author.objects.create(user=User.objects.get(username__exact="somename"),
                                     first_name="Somebody",
                                     last_name="Oncetoldme",
                                     info="Somebody info")

    def test_author_user(self):
        author = models.Author.objects.get(id=1)
        self.assertEqual(author.user, User.objects.get(id=1))

    def test_labels_max_length(self):
        author = models.Author.objects.get(id=1)
        self.assertEqual(author._meta.get_field('first_name').max_length, 100)
        self.assertEqual(author._meta.get_field('last_name').max_length, 100)
        self.assertEqual(author._meta.get_field('info').max_length, 1000)

    def test_get_absolute_url(self):
        author = models.Author.objects.get(id=1)
        self.assertEqual(author.get_absolute_url(), "/catalog/author/1")

    def test_str(self):
        author = models.Author.objects.get(id=1)
        self.assertEqual(str(author), f"{author.first_name} {author.last_name}")


class CategoryModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # parent category
        User.objects.create(username="somename", email="someemail@example.com", password="12345687")
        User.objects.create(username="somename2", email="someemail2@example.com", password="12345687")
        models.Category.objects.create(name="parent",
                                       info="some parent category",
                                       parent_category=None)
        parent_category = models.Category.objects.get(id=1)
        parent_category.users_subscribed.add(User.objects.get(username__exact="somename"))
        parent_category.save()

        # child category
        models.Category.objects.create(name="child",
                                       info="some child category",
                                       parent_category=parent_category)
        child_category = models.Category.objects.get(id=2)
        child_category.users_subscribed.add(User.objects.get(username__exact="somename2"))
        child_category.save()

    def test_str(self):
        category = models.Category.objects.get(id=2)
        self.assertEqual(str(category), category.name)

    def test_get_absolute_url(self):
        category = models.Category.objects.get(id=1)
        self.assertEqual(category.get_absolute_url(),
                         "/catalog/category/1")

    def test_get_absolute_url_for_subscribe(self):
        category = models.Category.objects.get(id=1)
        self.assertEqual(category.get_absolute_url_for_subscribe(),
                         "/catalog/category/1/subscribe")

    def test_labels(self):
        category = models.Category.objects.get(id=1)
        self.assertEqual(category._meta.get_field('name').max_length, 100)
        self.assertEqual(category._meta.get_field('info').max_length, 1000)

    def test_parent_category(self):
        category = models.Category.objects.get(id=2)
        parent_category = models.Category.objects.get(id=1)
        self.assertEqual(parent_category, category.parent_category)

    def test_users_subscribed(self):
        parent_category = models.Category.objects.get(id=1)
        child_category = models.Category.objects.get(id=2)

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
        models.Author.objects.create(user=User.objects.get(username__exact="someauthor"),
                                     first_name="Someauthor",
                                     last_name="Oncetoldme",
                                     info="Someauthor info")

        # parent category
        User.objects.create(username="somename", email="someemail@example.com", password="12345687")
        User.objects.create(username="somename2", email="someemail2@example.com", password="12345687")
        models.Category.objects.create(name="parent",
                                       info="some parent category",
                                       parent_category=None)
        parent_category = models.Category.objects.get(name__exact="parent")
        logging.critical(str(parent_category.id))
        parent_category.users_subscribed.add(User.objects.get(username__exact="somename"))
        parent_category.save()

        # child category
        models.Category.objects.create(name="child",
                                       info="some child category",
                                       parent_category=parent_category)
        child_category = models.Category.objects.get(name="child")
        child_category.users_subscribed.add(User.objects.get(username__exact="somename2"))
        child_category.save()

        models.EduMaterial.objects.create(title="Material 1",
                                          summary="Some material 1 in parent category",
                                          author=models.Author.objects.get(first_name="Someauthor"),
                                          access_type='p',
                                          pdf_file=File(open("pdfmaterials/some_pdf.pdf", 'rb')))
        edu_material = models.EduMaterial.objects.get(id=1)
        edu_material.category.add(child_category)

    def test_labels(self):
        material = models.EduMaterial.objects.get(id=1)
        self.assertEqual(material._meta.get_field('title').max_length, 200)
        self.assertEqual(material._meta.get_field('summary').max_length, 1000)
        self.assertEqual(material._meta.get_field('access_type').max_length, 1)

    def test_author(self):
        material = models.EduMaterial.objects.get(id=1)
        author = models.Author.objects.get(first_name='Someauthor')
        self.assertEqual(material.author, author)

    def test_str(self):
        material = models.EduMaterial.objects.get(id=1)
        self.assertEqual(str(material), material.title)

    def test_get_absolute_url(self):
        material = models.EduMaterial.objects.get(id=1)
        self.assertEqual(material.get_absolute_url(), "/catalog/material/1")

    def test_get_absolute_file_url(self):
        material = models.EduMaterial.objects.get(id=1)
        self.assertEqual(material.get_absolute_file_url(), "/catalog/material/1/file")


class UserRegisterFormTest(TestCase):
    def test_fields(self):
        form = forms.UserRegisterForm()
        self.assertEqual(form.fields['username'].label, 'Username')
        self.assertEqual(form.fields['email'].label, 'Email address')
        self.assertEqual(form.fields['first_name'].label, 'First name')
        self.assertEqual(form.fields['last_name'].label, 'Last name')
        self.assertEqual(form.fields['password1'].label, 'Password')
        self.assertEqual(form.fields['password2'].label, 'Password confirmation')


class GetUserCardDataFormTest(TestCase):
    def test_fields(self):
        form = forms.GetUserCardDataForm()
        self.assertEqual(form.fields["card_number"].label, "Card number field")
        self.assertEqual(form.fields["card_expiry"].label, "Expiration Date")
        self.assertEqual(form.fields["card_code"].label, "CVV/CVC")


class IndexViewTest(TestCase):
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/catalog/')
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template_and_is_accessible_by_name(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/index.html')


class EduMaterialCreateViewTest(TestCase):
    def setUp(self):
        # we need:

        # an author
        # who is also a user
        # material data
        # and a category for the test material (actually two categories, parent and child)
        # a user who is subscribed to the category
        test_user = User.objects.create_user(username="testuser", email="testuser@example.com", password="passwodr")
        test_author = models.Author.objects.create(user=test_user,
                                                   first_name="Test",
                                                   last_name="Author",
                                                   info="Some test author")
        test_user_not_author = User.objects.create_user(username="user1",
                                                        email="user1@example.com",
                                                        password="passwodr")
        test_user_not_author2 = User.objects.create_user(username="user2",
                                                         email="user2@example.com",
                                                         password="passwodr")

