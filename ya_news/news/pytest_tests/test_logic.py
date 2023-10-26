"""Тестирование логики."""
from http import HTTPStatus
from random import choice

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from conftest import COMMENT_TEXT
from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, form_data, detail_url):
    """Тест анонимный пользователь не может отправить комментарий."""
    comment_count_before_create = Comment.objects.count()
    client.post(detail_url, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == comment_count_before_create


@pytest.mark.django_db
def test_user_can_create_comment(author_client, form_data, detail_url):
    """Тест aвторизованный пользователь может отправить комментарий."""
    comment_count_before_create = Comment.objects.count()
    response = author_client.post(detail_url, data=form_data)
    assertRedirects(response, f'{detail_url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count > comment_count_before_create
    comment = Comment.objects.get()
    assert comment.text == COMMENT_TEXT
    assert comment.author == form_data['author']
    assert comment.news == form_data['news']


def test_user_cant_use_bad_words(admin_client, detail_url):
    """
    Тест если комментарий содержит
    запрещённые слова, он не будет опубликован.
    """
    comment_count_before_create = Comment.objects.count()
    bad_words_data = {'text': f'Какой-то текст, '
                              f'{choice(BAD_WORDS)}, '
                              f'еще текст'}
    response = admin_client.post(detail_url, data=bad_words_data)
    assertFormError(response, 'form', 'text', errors=WARNING)
    comments_count = Comment.objects.count()
    assert comments_count == comment_count_before_create


def test_author_can_edit_comment(author_client,
                                 comment,
                                 edit_url,
                                 form_data,
                                 url_to_comments):
    """Тест автор может редактировать свой комментарий."""
    response = author_client.post(edit_url, data=form_data)
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == COMMENT_TEXT


def test_user_cant_edit_comment_of_another_user(admin_client,
                                                comment,
                                                edit_url,
                                                form_data,
                                                url_to_comments):
    """Тест редактирование комментария недоступно для другого пользователя."""
    response = admin_client.post(edit_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text
    assert comment.news == comment_from_db.news
    assert comment.author == comment_from_db.author


def test_author_can_delete_comment(author_client,
                                   comment,
                                   delete_url,
                                   url_to_comments):
    """Тест автор может удалить свой комментарий."""
    comment_count_before_delete = Comment.objects.count()
    response = author_client.delete(delete_url)
    assertRedirects(response, url_to_comments)
    comments_count = Comment.objects.count()
    assert comments_count < comment_count_before_delete


def test_user_cant_delete_comment_of_another_user(admin_client,
                                                  comment,
                                                  delete_url):
    """Тест удаление комментария недоступно для другого пользователя."""
    comment_count_before_delete = Comment.objects.count()
    response = admin_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == comment_count_before_delete
