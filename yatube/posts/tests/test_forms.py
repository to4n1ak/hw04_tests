from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='testauthor')
        cls.group = Group.objects.create(
            title='Тестовая группа No1',
            slug='testgroup1',
            description='Описание тестовой группы No1',
        )
        cls.post1 = Post.objects.create(
            author=cls.user,
            text='Тестовый пост No1',
            group=cls.group,
        )

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.user)

    """Задание из Практикума "Тестирование Forms":"""
    def test_post_edit(self):
        """Проверка редактирования существующего поста"""
        total_posts = Post.objects.count()
        new_post = {'text': 'Обновлённый пост'}
        self.author_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post1.id}),
            data=new_post,
            follow=True)
        self.post1.refresh_from_db()
        self.assertEqual(self.post1.text, 'Обновлённый пост')
        self.assertEqual(Post.objects.count(), total_posts)

    def test_new_post_create(self):
        """Проверка создания нового поста"""
        total_posts = Post.objects.count()
        self.author_client.post(
            reverse('posts:post_create'),
            data={'text': 'Тестовый пост No2',
                  'author': self.user.username,
                  'group': self.group.id,
                  },
            follow=True)
        self.assertEqual(Post.objects.count(), total_posts + 1)
