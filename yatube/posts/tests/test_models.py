from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='testgroup',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )


    """Задание из Практикума "Тестирование моделей":"""
    def test_models_group_correct_str(self):
        """Проверяем, что у модели Group корректно работает __str__."""
        group = PostModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))


    def test_models_post_correct_str(self):
        """Проверяем, что у модели Post корректно работает __str__."""
        post = PostModelTest.post
        expected_object_name = post.text
        self.assertEqual(expected_object_name, str(post))


    def test_verbose_name_group(self):
        """Проверяем verbose_names у модели Group."""
        group = PostModelTest.group
        field_verboses = {
            'title': 'Наименование сообщества',
            'slug': 'Уникальный адрес сообщества',
            'description': 'Описание сообщества',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).verbose_name, expected_value)


    def test_verbose_name_post(self):
        """Проверяем verbose_names у модели Post."""
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст сообщения',
            'pub_date': 'Дата публикации',
            'author': 'Автор сообщения',
            'group': 'Сообщество',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value)
