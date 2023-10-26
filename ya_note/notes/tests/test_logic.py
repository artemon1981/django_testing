"""Тесты логики приложения"""
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
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
                                       author=cls.author)
        cls.url_success = reverse('notes:success')
        cls.url_add_note = reverse('notes:add')
        cls.url_edit = reverse('notes:edit', args=(cls.note.slug,))
        cls.url_delete = reverse('notes:delete', args=(cls.note.slug,))
        cls.login_url = reverse('users:login')
        cls.form_data = {'title': 'Новый заголовок',
                         'text': 'Новый текст',
                         'slug': 'new-slug'}

    def test_user_can_create_note(self):
        """Тест залогиненный пользователь может создать заметку."""
        self.client.force_login(self.author)
        notes_count_before_create = Note.objects.count()
        response = self.client.post(self.url_add_note, data=self.form_data)
        self.assertRedirects(response, self.url_success)
        notes_count = Note.objects.count()
        new_note = Note.objects.last()
        self.assertGreater(notes_count, notes_count_before_create)
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        """Тест анонимный пользователь не может создать заметку."""
        notes_count_before_create = Note.objects.count()
        response = self.client.post(self.url_add_note, data=self.form_data)
        expected_url = f'{self.login_url}?next={self.url_add_note}'
        self.assertRedirects(response, expected_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, notes_count_before_create)

    def test_not_unique_slug(self):
        """Тест невозможности создания одинаковых slug."""
        notes_count_before_create = Note.objects.count()
        self.client.force_login(self.author)
        self.form_data['slug'] = self.note.slug
        self.client.post(self.url_add_note, data=self.form_data)
        response = self.client.post(self.url_add_note, data=self.form_data)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=(self.note.slug + WARNING))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, notes_count_before_create)

    def test_empty_slug(self):
        """
        Тест при создании заметки не заполнен slug,
        то он формируется автоматически.
        """
        notes_count_before_create = Note.objects.count()
        self.form_data.pop('slug')
        self.client.force_login(self.author)
        response = self.client.post(self.url_add_note, data=self.form_data)
        self.assertRedirects(response, self.url_success)
        notes_count = Note.objects.count()
        self.assertGreater(notes_count, notes_count_before_create)
        new_note = Note.objects.get(pk=2)
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_edit_note(self):
        """Тест автор может редактировать заметку."""
        self.client.force_login(self.author)
        response = self.client.post(self.url_edit, self.form_data)
        self.assertRedirects(response, self.url_success)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.slug, self.form_data['slug'])

    def test_other_user_cant_edit_note(self):
        """
        Тест зарегистрированный пользователь
        не может редактировать чужую заметку.
        """
        self.client.force_login(self.auth_user)
        response = self.client.post(self.url_edit, self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.slug, note_from_db.slug)

    def test_author_can_delete_note(self):
        """Тест автор может удалить свою заметку."""
        notes_count_before_delete = Note.objects.count()
        self.client.force_login(self.author)
        response = self.client.post(self.url_delete)
        self.assertRedirects(response, self.url_success)
        notes_count = Note.objects.count()
        self.assertLess(notes_count, notes_count_before_delete)

    def test_other_user_cant_delete_note(self):
        """Тест не автор не может удалить заметку."""
        notes_count_before_delete = Note.objects.count()
        self.client.force_login(self.auth_user)
        response = self.client.post(self.url_delete)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, notes_count_before_delete)
