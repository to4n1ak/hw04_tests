from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms
from django.conf import settings

from ..models import Group, Post

User = get_user_model()
TEST_POSTS_TOTAL = 15  # Создание постов для тестирования


class PostViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='testauthor')
        cls.author_client = Client()
        cls.author_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Тестовая группа No1',
            slug='testgroup1',
            description='Описание тестовой группы No1',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост No1',
            group=cls.group,
        )

    """Задание из Практикума "Тестирование Views" No1:"""
    def test_pages_use_correct_template(self):
        """Проверка на использование корректного шаблона."""
        templates_page_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug':
                            f'{self.group.slug}'}): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username':
                            f'{self.user.username}'}): 'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id':
                            f'{self.post.id}'}): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit',
                    kwargs={'post_id':
                            f'{self.post.id}'}): 'posts/create_post.html',
        }
        for reverse_address, template in templates_page_names.items():
            with self.subTest(reverse_address=reverse_address):
                response = self.author_client.get(reverse_address)
                error = (f'Адрес {reverse_address} - '
                         f'не соответствует шаблону {template}'
                         )
                self.assertTemplateUsed(response, template, error)

    """Задание из Практикума "Тестирование Views" No2:"""
    def check_method(self, post):  # метод для проверок
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.group.id, self.post.group.id)

    def test_index_correct_context(self):
        """Проверка шаблона "index" на контекст."""
        response = self.author_client.get(reverse("posts:index"))
        self.check_method(response.context["page_obj"][0])

    def test_group_list_correct_context(self):
        """Проверка шаблона "group_list" на контекст."""
        response = self.author_client.get(
            reverse("posts:group_list", kwargs={"slug": self.group.slug})
        )
        self.assertEqual(response.context["group"], self.group)
        self.check_method(response.context["page_obj"][0])

    def test_profile_correct_context(self):
        """Проверка шаблона "profile" на контекст."""
        response = self.author_client.get(
            reverse("posts:profile", kwargs={"username": self.user.username})
        )
        self.assertEqual(response.context["author"], self.user)
        self.check_method(response.context["page_obj"][0])

    def test_post_detail_correct_context(self):
        """Проверка шаблона "post_detail" на контекст."""
        response = self.author_client.get(
            reverse("posts:post_detail", kwargs={"post_id": self.post.id})
        )
        self.check_method(response.context["post"])

    def test_post_create_correct_context(self):
        """Проверка шаблона "post_create" на контекст."""
        response = self.author_client.get(reverse('posts:post_create'))
        result = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in result.items():
            with self.subTest(value=value):
                final_result = response.context.get('form').fields.get(value)
                self.assertIsInstance(final_result, expected)

    def test_post_edit_correct_context(self):
        """Проверка шаблона "post_edit" на контекст."""
        response = self.author_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}))
        result = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in result.items():
            with self.subTest(value=value):
                final_result = response.context.get('form').fields.get(value)
                self.assertIsInstance(final_result, expected)
        self.assertTrue(response.context.get('is_edit'))

    """Задание из Практикума "Тестирование Views" No3:"""
    def test_new_post(self):
        """Проверка создания нового поста"""
        post = Post.objects.create(
            text='Текст поста для проверки',
            author=self.user,
            group=self.group,
        )
        self.post.refresh_from_db()
        response_index = self.author_client.get(
            reverse('posts:index'))
        response_group = self.author_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': f'{self.group.slug}'}))
        response_profile = self.author_client.get(
            reverse('posts:profile',
                    kwargs={'username': f'{self.user.username}'}))
        index = response_index.context['page_obj']
        group = response_group.context['page_obj']
        profile = response_profile.context['page_obj']
        self.assertIn(post, index)
        self.assertIn(post, group)
        self.assertIn(post, profile)


"""Задание из Практикума "Тестирование Views" No4:"""


class PaginatorTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='testauthor')
        cls.author_client = Client()
        cls.author_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Тестовая группа No1',
            slug='testgroup1',
            description='Описание тестовой группы No1',
        )

    def setUp(self):  # Создание постов для тестирования паджинатора
        new_posts = []
        for i in range(TEST_POSTS_TOTAL):
            new_posts.append(Post(author=self.user,
                                  text=f'Тестовый пост No{i}',
                                  group=self.group))
        Post.objects.bulk_create(new_posts)

    def test_paginator_first_page_ten_posts(self):
        """Проверка вывода кол-ва сообщений."""
        pages = (
            reverse('posts:index'),
            reverse('posts:group_list',
                    kwargs={'slug': f'{self.group.slug}'}),
            reverse('posts:profile',
                    kwargs={'username': f'{self.user.username}'})
        )
        for page in pages:
            response_1st_page = self.author_client.get(page)
            response_2nd_page = self.author_client.get(page + '?page=2')
        count_posts_1st_page = len(response_1st_page.context['page_obj'])
        count_posts_2nd_page = len(response_2nd_page.context['page_obj'])
        self.assertEqual(count_posts_1st_page, settings.POST_PER_PAGE)
        self.assertEqual(count_posts_2nd_page,
                         Post.objects.count() - settings.POST_PER_PAGE)
