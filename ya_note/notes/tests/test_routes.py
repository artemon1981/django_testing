"""Тесты доступности маршрутов."""
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):
    """Класс проверки маршрутов."""
    @classmethod
    def setUpTestData(cls):
        """Переменные класса."""
        cls.user_client = Client()
        cls.auth_user = User.objects.create(username='testUser')
        cls.author = User.objects.create(username='testAuthor')
        cls.reader = User.objects.create(username='testReader')
        cls.note = Note.objects.create(title='Заголовок',
                                       text='Текст',
                                       slug='slug',
                                       author=cls.author)

    def test_home_page(self):
        """Тест проверки доступности страниц всем."""
        for name in ('notes:home',
                     'users:login',
                     'users:logout',
                     'users:signup'):
            url = reverse(name)
            response = self.client.get(url)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_user(self):
        """Тест доступности страниц аутентифицированному пользователю."""
        self.client.force_login(self.auth_user)
        for name in ('notes:list', 'notes:add', 'notes:success'):
            url = reverse(name)
            response = self.client.get(url)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_authors(self):
        """
        Тест страницы отдельной заметки,
        удаления и редактирования заметки доступны автору.
        """
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),)

        for user, status in users_statuses:
            self.client.force_login(user)
            for name in ('notes:detail', 'notes:edit', 'notes:delete'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """Тест анонимный пользователь перенаправляется на страницу логина."""
        login_url = reverse('users:login')
        name_pages = (('notes:detail', (self.note.slug,)),
                      ('notes:edit', (self.note.slug,)),
                      ('notes:delete', (self.note.slug,)),
                      ('notes:add', None),
                      ('notes:success', None),
                      ('notes:list', None),)
        for name, args in name_pages:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
