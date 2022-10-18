from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from ..models import Group, Post

User = get_user_model()
POST_PER_PAGE = 10  # Кол-во постов на странице
POSTS_2ND_PAGE = 5  # Постов на второй странице (проверка паджинатора)


class PostViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='testauthor')
        cls.group = Group.objects.create(
            title = 'Тестовая группа No1',
            slug = 'testgroup1',
            description = 'Описание тестовой группы No1',
        )

        for i in range(1,16):
            cls.post = Post.objects.create(
                author = cls.user,
                text = f'Тестовый пост No{i}',
                group = cls.group,
                )

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.user)


    """Задание из Практикума "Тестирование Views" No1:"""
    def test_pages_use_correct_template(self):
        """Проверка на использование корректного шаблона."""
        templates_page_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': f'{self.group.slug}'}): 'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': f'{self.user.username}'}): 'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': f'{self.post.id}'}): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit', kwargs={'post_id': f'{self.post.id}'}): 'posts/create_post.html',
        }
        for reverse_address, template in templates_page_names.items():
            with self.subTest(reverse_address=reverse_address):
                response = self.author_client.get(reverse_address)
                error = (f'Адрес {reverse_address} - '
                f'не соответствует шаблону {template}'
                )
                self.assertTemplateUsed(response, template, error)
 
    
    """Задание из Практикума "Тестирование Views" No2:"""
    def test_post_detail_correct_context(self):
        """Проверка шаблона "post_detail" на контекст."""
        response = self.author_client.get(reverse('posts:post_detail', kwargs={'post_id': self.post.id}))
        post_text_0 = {response.context['post'].text: 'Тестовый пост No1',
                       response.context['post'].group: self.group,
                       response.context['post'].author: PostViewsTest.user
                       }
        for value, expected in post_text_0.items():
            self.assertEqual(post_text_0[value], expected)
    

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
    def test_paginator_first_page_ten_posts(self):
        """Проверка вывода 10 сообщений."""
        response = (
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': f'{self.group.slug}'}),
            reverse('posts:profile', kwargs={'username': f'{self.user.username}'})
        )
        for reverse_name in response:
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name)
                self.assertEqual(
                    len(response.context['page_obj'].object_list), POST_PER_PAGE
                )


    def test_paginator_second_page(self):
        """Проверка вывода сообщений на второй странице."""
        response = (
            (reverse('posts:index') + '?page=2'),
            (reverse('posts:group_list', kwargs={'slug': f'{self.group.slug}'}) + '?page=2'),
            (reverse('posts:profile', kwargs={'username': f'{self.user.username}'}) + '?page=2')
        )
        for reverse_name in response:
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name)
                self.assertEqual(
                    len(response.context['page_obj'].object_list), POSTS_2ND_PAGE
                )
    

    """Задание из Практикума "Тестирование Views" No4:"""
    def test_new_post(self):
        """Проверка создания нового поста"""
        post = Post.objects.create(
            text='Текст поста для проверки',
            author=self.user,
            group=self.group,
            )
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
