"""Тестирование контента."""
from django.conf import settings
from django.urls import reverse

FORM = 'form'


def test_news_count(client, news_for_sort):
    """Тест Количество новостей на главной странице — не более 10."""
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, news_for_sort):
    """Тест сортировки на главной странице."""
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments_order(author_client, comment_for_sort, news, detail_url):
    """
    Тест комментарии на странице отдельной
    новости отсортированы в хронологическом порядке.
    """
    response = author_client.get(detail_url)
    assert 'news' in response.context
    news = response.context['news']
    comment_first, comment_second = news.comment_set.all()
    assert comment_first.created < comment_second.created


def test_anonymous_client_has_no_form(client, detail_url):
    """Тест у анонимного пользователя в контексте нет формы."""
    response = client.get(detail_url)
    assert FORM not in response.context


def test_authorized_client_has_form(author_client, detail_url):
    """Тест у автора в контексте есть форма."""
    response = author_client.get(detail_url)
    assert FORM in response.context
