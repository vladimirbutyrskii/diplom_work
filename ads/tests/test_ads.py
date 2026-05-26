import pytest
from django.urls import reverse
from rest_framework import status

from ads.models import Ad, Comment


# ============================================
# ТЕСТЫ ОБЪЯВЛЕНИЙ
# ============================================

class TestAdList:
    """Тесты получения списка объявлений."""

    @pytest.mark.django_db
    def test_list_ads_empty(self, api_client):
        """Получение пустого списка объявлений."""
        url = reverse('ads-list')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['results'] == []

    def test_list_ads_with_data(self, api_client, ad):
        """Получение списка объявлений с данными."""
        url = reverse('ads-list')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['title'] == ad.title

    @pytest.mark.django_db
    def test_list_ads_unauthorized(self, api_client):
        """Анонимный пользователь может видеть список объявлений."""
        url = reverse('ads-list')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK


class TestAdCreate:
    """Тесты создания объявлений."""

    def test_create_ad_authenticated(self, user_client, ad_data):
        """Авторизованный пользователь может создать объявление."""
        url = reverse('ads-list')
        response = user_client.post(url, ad_data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == ad_data['title']
        assert response.data['price'] == ad_data['price']
        assert Ad.objects.count() == 1

    @pytest.mark.django_db
    def test_create_ad_unauthorized(self, api_client, ad_data):
        """Анонимный пользователь не может создать объявление."""
        url = reverse('ads-list')
        response = api_client.post(url, ad_data, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert Ad.objects.count() == 0

    def test_create_ad_missing_fields(self, user_client):
        """Создание объявления без обязательных полей."""
        url = reverse('ads-list')
        response = user_client.post(url, {}, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'title' in response.data
        assert 'price' in response.data


class TestAdRetrieve:
    """Тесты получения одного объявления."""

    def test_retrieve_ad(self, api_client, ad):
        """Получение объявления по ID."""
        url = reverse('ads-detail', args=[ad.id])
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == ad.title
        assert response.data['description'] == ad.description
        assert 'comments' in response.data

    @pytest.mark.django_db
    def test_retrieve_nonexistent_ad(self, api_client):
        """Попытка получить несуществующее объявление."""
        url = reverse('ads-detail', args=[9999])
        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestAdUpdate:
    """Тесты редактирования объявлений."""

    def test_update_own_ad(self, user_client, ad):
        """Пользователь может редактировать своё объявление."""
        url = reverse('ads-detail', args=[ad.id])
        response = user_client.patch(url, {'title': 'Новое название'}, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'Новое название'

    def test_update_other_user_ad(self, user_client, admin, ad):
        """Пользователь не может редактировать чужое объявление."""
        # Создаём объявление от имени админа
        other_ad = Ad.objects.create(
            author=admin,
            title='Чужое объявление',
            price=10000,
            description='Не трогать',
        )
        url = reverse('ads-detail', args=[other_ad.id])
        response = user_client.patch(url, {'title': 'Взломано'}, format='json')

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_any_ad_by_admin(self, admin_client, ad):
        """Администратор может редактировать любое объявление."""
        url = reverse('ads-detail', args=[ad.id])
        response = admin_client.patch(url, {'title': 'Отредактировано админом'}, format='json')

        assert response.status_code == status.HTTP_200_OK


class TestAdDelete:
    """Тесты удаления объявлений."""

    def test_delete_own_ad(self, user_client, ad):
        """Пользователь может удалить своё объявление."""
        url = reverse('ads-detail', args=[ad.id])
        response = user_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Ad.objects.count() == 0

    def test_delete_other_user_ad(self, user_client, admin):
        """Пользователь не может удалить чужое объявление."""
        other_ad = Ad.objects.create(
            author=admin,
            title='Чужое объявление',
            price=10000,
            description='Не трогать',
        )
        url = reverse('ads-detail', args=[other_ad.id])
        response = user_client.delete(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Ad.objects.count() == 1

    def test_delete_any_ad_by_admin(self, admin_client, ad):
        """Администратор может удалить любое объявление."""
        url = reverse('ads-detail', args=[ad.id])
        response = admin_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Ad.objects.count() == 0


class TestAdSearch:
    """Тесты поиска объявлений."""

    @pytest.fixture(autouse=True)
    def setup_ads(self, user):
        """Создаём несколько объявлений для поиска."""
        Ad.objects.create(author=user, title='Продам гараж', price=50000, description='Кирпичный')
        Ad.objects.create(author=user, title='Куплю автомобиль', price=100000, description='Срочно')
        Ad.objects.create(author=user, title='Сдам квартиру', price=30000, description='На длительный срок')

    def test_search_by_title(self, api_client):
        """Поиск объявления по названию."""
        url = reverse('ads-list') + '?search=гараж'
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['title'] == 'Продам гараж'

    def test_search_no_results(self, api_client):
        """Поиск по несуществующему названию."""
        url = reverse('ads-list') + '?search=вертолёт'
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 0

    def test_filter_by_title(self, api_client):
        """Фильтрация объявлений по названию."""
        url = reverse('ads-list') + '?title=автомобиль'
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert 'автомобиль' in response.data['results'][0]['title']


class TestAdPagination:
    """Тесты пагинации объявлений."""

    def test_pagination_limit(self, api_client, user):
        """Проверка, что на странице не более 4 объявлений."""
        # Создаём 6 объявлений
        for i in range(6):
            Ad.objects.create(
                author=user,
                title=f'Объявление {i}',
                price=1000 + i * 100,
                description=f'Описание {i}',
            )

        url = reverse('ads-list')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 4
        assert response.data['count'] == 6
        assert response.data['next'] is not None

    def test_pagination_second_page(self, api_client, user):
        """Проверка второй страницы пагинации."""
        for i in range(6):
            Ad.objects.create(
                author=user,
                title=f'Объявление {i}',
                price=1000 + i * 100,
                description=f'Описание {i}',
            )

        url = reverse('ads-list') + '?page=2'
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
        assert response.data['previous'] is not None
        assert response.data['next'] is None


# ============================================
# ТЕСТЫ ОТЗЫВОВ
# ============================================

class TestCommentList:
    """Тесты получения списка отзывов."""

    @pytest.mark.django_db(transaction=True)
    def test_list_comments_authenticated(self, user_client, ad, comment):
        """Авторизованный пользователь может видеть отзывы."""
        from ads.models import Comment
        url = reverse('ad-comments-list', args=[ad.id])
        response = user_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        # comment (1) + 4 из фикстур = минимум 1, проверяем что список не пустой
        assert len(response.data) >= 1

    @pytest.mark.django_db
    def test_list_comments_unauthorized(self, api_client, ad):
        url = reverse('ad-comments-list', args=[ad.id])
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestCommentCreate:
    """Тесты создания отзывов."""

    @pytest.mark.django_db(transaction=True)
    def test_create_comment_authenticated(self, user_client, comment_data):
        """Авторизованный пользователь может создать отзыв."""
        from ads.models import Ad
        new_ad = Ad.objects.create(
            author=user_client.user,
            title='Объявление для отзыва',
            price=2000,
            description='Тест'
        )
        url = reverse('ad-comments-list', args=[new_ad.id])
        response = user_client.post(url, comment_data, format='json')
        print(f'\nDEBUG response: {response.data}')  # Посмотри, что возвращает сервер
        assert response.status_code == status.HTTP_201_CREATED

    @pytest.mark.django_db
    def test_create_comment_unauthorized(self, api_client, ad, comment_data):
        url = reverse('ad-comments-list', args=[ad.id])
        response = api_client.post(url, comment_data, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestCommentUpdate:
    """Тесты редактирования отзывов."""

    def test_update_own_comment(self, user_client, ad, comment):
        """Пользователь может редактировать свой отзыв."""
        url = reverse('ad-comments-detail', args=[ad.id, comment.id])
        response = user_client.patch(url, {'text': 'Обновлённый отзыв'}, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['text'] == 'Обновлённый отзыв'

    def test_update_other_user_comment(self, user_client, ad, admin):
        """Пользователь не может редактировать чужой отзыв."""
        other_comment = Comment.objects.create(
            author=admin,
            ad=ad,
            text='Отзыв админа',
        )
        url = reverse('ad-comments-detail', args=[ad.id, other_comment.id])
        response = user_client.patch(url, {'text': 'Взлом'}, format='json')

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_any_comment_by_admin(self, admin_client, ad, comment):
        """Администратор может редактировать любой отзыв."""
        url = reverse('ad-comments-detail', args=[ad.id, comment.id])
        response = admin_client.patch(url, {'text': 'Отредактировано админом'}, format='json')

        assert response.status_code == status.HTTP_200_OK


class TestCommentDelete:
    """Тесты удаления отзывов."""

    def test_delete_own_comment(self, user_client, ad, comment):
        """Пользователь может удалить свой отзыв."""
        url = reverse('ad-comments-detail', args=[ad.id, comment.id])
        response = user_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Comment.objects.count() == 0

    def test_delete_other_user_comment(self, user_client, ad, admin):
        """Пользователь не может удалить чужой отзыв."""
        other_comment = Comment.objects.create(
            author=admin,
            ad=ad,
            text='Отзыв админа',
        )
        url = reverse('ad-comments-detail', args=[ad.id, other_comment.id])
        response = user_client.delete(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_any_comment_by_admin(self, admin_client, ad, comment):
        """Администратор может удалить любой отзыв."""
        url = reverse('ad-comments-detail', args=[ad.id, comment.id])
        response = admin_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Comment.objects.count() == 0

