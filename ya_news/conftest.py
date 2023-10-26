import pytest

from datetime import datetime, timedelta

from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from news.models import Comment, News

COMMENT_TEXT = 'Текст комментария новый'


@pytest.fixture
def author(django_user_model):
    """Создаем модель автора."""
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    """Логиним автора."""
    client.force_login(author)
    return client


@pytest.fixture
def news(author):
    """Создаем  объект новости."""
    news = News.objects.create(title='Заголовок',
                               text='Текст')
    return news


@pytest.fixture
def comment(author, news):
    """Создаем объект комментария."""
    comment = Comment.objects.create(news=news,
                                     author=author,
                                     text='Текст комментария')
    return comment


@pytest.fixture
def news_11(author):
    """Создаем одинадцать новостей."""
    today = datetime.today()
    news_11 = News.objects.bulk_create(
        News(title=f'Новость {index}',
             text='Просто текст.',
             date=today - timedelta(days=index))
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1))
    return news_11


@pytest.fixture
def comment_2(author, news):
    """Создаем два комментария."""
    now = timezone.now()
    for index in range(2):
        comment_2 = Comment.objects.create(
            news=news, author=author, text=f'Tекст {index}',
        )
        comment_2.created = now + timedelta(days=index)
        comment_2.save()
    return comment_2


@pytest.fixture
def detail_url(news):
    """Урл одиночной записи"""
    detail_url = reverse('news:detail', args=(news.id,))
    return detail_url


@pytest.fixture
def form_data(author, news):
    """Форма для POST запроса."""
    return {'text': COMMENT_TEXT,
            'author': author,
            'news': news
            }


@pytest.fixture
def edit_url(comment):
    """Урл редактирования комментария."""
    edit_url = reverse('news:edit', args=(comment.id,))
    return edit_url


@pytest.fixture
def delete_url(comment):
    """Урл удаления комментария."""
    delete_url = reverse('news:delete', args=(comment.id,))
    return delete_url


@pytest.fixture
def url_to_comments(news):
    """Урл блока с комментариями."""
    url_to_comments = reverse('news:detail', args=(news.id,)) + '#comments'
    return url_to_comments
