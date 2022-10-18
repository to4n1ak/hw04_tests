from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from ..models import Group, Post

User = get_user_model()


class PostURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='testauthor')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='testgroup',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )

    def setUp(self):
        #  Создаем неавторизованный клиент
        self.guest_client = Client()
        #  Создаем клиент для автора поста
        self.author_client = Client()
        self.author_client.force_login(self.user)
        #  Создаем пользователя и клиент для проверки просмотра
        self.user2 = User.objects.create_user(username='testviewer')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user2)

    """Задание из Практикума "Тестирование URLs":"""
    def test_unauthorized_urls(self):
        """Проверка URL-адресов неавторизованным пользователем"""
        pages = [
            '/', '/group/testgroup/', '/profile/testauthor/', '/posts/1/',
        ]
        for page in pages:
            with self.subTest(page=page):
                response = self.guest_client.get(page)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_author_urls(self):
        """Проверка URL-адресов авторизованным автором поста"""
        pages = [
            '/', '/group/testgroup/', '/profile/testauthor/',
            '/posts/1/', '/create/', '/posts/1/edit/',
        ]
        for page in pages:
            with self.subTest(page=page):
                response = self.author_client.get(page)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_auth_user_redirect(self):
        """Проверка редиректа пользователя
        при редактировании чужого поста
        """
        response = self.authorized_client.get('/posts/1/edit/', follow=True)
        self.assertRedirects(response, '/posts/1/')

    def test_unregistered_redirect(self):
        """Проверка редиректа неавторизованного пользователя"""
        redirect_pages = {
            '/create/': '/auth/login/?next=/create/',
            '/posts/1/edit/': '/auth/login/?next=/posts/1/edit/',
        }
        for page, redirect_page in redirect_pages.items():
            with self.subTest(page=page):
                response = self.guest_client.get(page)
                self.assertRedirects(response, redirect_page)

    def test_non_existing_page(self):
        """Проверка ответа от несуществующей страницы"""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, 404)

    def test_urls_correct_template(self):
        """Проверка шаблонов"""
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/testgroup/': 'posts/group_list.html',
            '/profile/testauthor/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            '/posts/1/edit/': 'posts/create_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.author_client.get(address)
                self.assertTemplateUsed(response, template)
