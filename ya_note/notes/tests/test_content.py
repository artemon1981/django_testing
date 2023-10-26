"""Тесты проверки контекста"""
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):
    """Класс проверки контента."""

    @classmethod
    def setUpTestData(cls):
        """Переменные класса."""
        cls.user_client = Client()
        cls.auth_user = User.objects.create(username='testUser')
        cls.author = User.objects.create(username='testAuthor')
        cls.note = Note.objects.create(title='Заголовок',
                                       text='Текст',
                                       slug='slug',
                                       author=cls.author)

    def test_note_in_list_for_author(self):
        """
        Тест заметка передаётся на страницу со списком заметок
        в списке object_list в словаре context.
        """
        self.client.force_login(self.author)
        url = reverse('notes:list')
        response = self.client.get(url)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)

    def test_notes_list_for_different_users(self):
        """
        Тест в список заметок одного пользователя
        не попадают заметки другого пользователя.
        """
        self.client.force_login(self.author)
        url = reverse('notes:list')
        response = self.client.get(url)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)
        self.client.force_login(self.auth_user)
        response = self.client.get(url)
        object_list = response.context['object_list']
        self.assertNotIn(self.note, object_list)

    def test_create_note_page_contains_form(self):
        """
        Тест на страницы создания и
        редактирования заметки передаются формы.
        """
        self.client.force_login(self.author)
        name_pages = (('notes:edit', (self.note.slug,)),
                      ('notes:add', None),)
        for name, args in name_pages:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertIn('form', response.context)
