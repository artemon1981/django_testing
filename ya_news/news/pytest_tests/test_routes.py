"""Тестирование маршрутов."""
import pytest

from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.parametrize('name',
                         ('news:home',
                          'users:login',
                          'users:logout',
                          'users:signup'), )
def test_home_availability_for_anonymous_user(client, name, news):
    """Тест страницы доступны анонимному пользователю."""
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


def test_pages_availability_for_auth_user(admin_client, news):
    """
    Тест страница отдельной новости
    доступна анонимному пользователю.
    """
    url = reverse('news:detail', args=(news.id,))
    response = admin_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize('parametrized_client, expected_status',
                         ((pytest.lazy_fixture('admin_client'),
                           HTTPStatus.NOT_FOUND),
                          (pytest.lazy_fixture('author_client'),
                           HTTPStatus.OK)), )
@pytest.mark.parametrize('name',
                         ('news:edit', 'news:delete'), )
def test_pages_availability_for_different_users(parametrized_client,
                                                name,
                                                news,
                                                comment,
                                                expected_status):
    """
    Тест страницы редактирования и удаления
    комментария доступны автору комментария,
    но недоступны другому пользователю.
    """
    url = reverse(name, args=(comment.id,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize('name',
                         ('news:edit', 'news:delete'), )
def test_redirect_for_anonymous_client(name, news, comment, client):
    """
    Тест при попытке перейти на страницу редактирования
    или удаления комментария анонимный пользователь
    перенаправляется на страницу авторизации.
    """
    login_url = reverse('users:login')
    url = reverse(name, args=(comment.id,))
    redirect_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, redirect_url)
