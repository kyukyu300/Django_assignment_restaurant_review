from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APITestCase
from django.urls import reverse

from restaurants.models import Restaurant
from reviews.models import Review

User = get_user_model()


class ReviewModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', nickname='testuser', password='password1234')
        self.restaurant = Restaurant.objects.create(
            name="Test Restaurant",
            description="Test Description",
            address="Test Address",
            contact="Test Contact",
            open_time="10:00:00",
            close_time="22:00:00",
            last_order="21:00:00",
            regular_holiday="MON"
        )
        self.test_review = {
            'user': self.user,
            'restaurant': self.restaurant,
            'title': "충칭 키친",
            'comment': "완전 맛있어요"
        }

    def test_create_review(self):
        review = Review.objects.create(**self.test_review)
        self.assertEqual(Review.objects.count(), 1)
        self.assertEqual(review.user, self.user)
        self.assertEqual(review.restaurant, self.restaurant)
        self.assertEqual(review.title, self.test_review['title'])
        self.assertEqual(review.comment, self.test_review['comment'])


class ReviewAPIViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', nickname='testuser', password='password1234')
        self.client.force_login(self.user)  # ✅ 로그인 처리

        self.restaurant = Restaurant.objects.create(
            name="Test Restaurant",
            description="Test Description",
            address="Test Address",
            contact="Test Contact",
            open_time="10:00:00",
            close_time="22:00:00",
            last_order="21:00:00",
            regular_holiday="MON"
        )

        self.test_review = {
            'user': self.user,
            'restaurant': self.restaurant,
            'title': "충칭 키친",
            'comment': "완전 맛있어요"
        }

    def test_get_review_list(self):
        self.review = Review.objects.create(**self.test_review)
        url = reverse('review-list', kwargs={'restaurant_id': self.restaurant.id})

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data.get('results')), 1)
        self.assertEqual(response.data.get('results')[0].get('title'), self.review.title)
        self.assertEqual(response.data.get('results')[0].get('comment'), self.review.comment)
        self.assertEqual(response.data.get('results')[0].get('user')['id'], self.review.user.id)
        self.assertEqual(response.data.get('results')[0].get('restaurant'), self.review.restaurant.id)

    def test_post_review(self):
        url = reverse('review-list', kwargs={'restaurant_id': self.restaurant.id})
        data = {
            'title': "충칭 키친",
            'comment': "완전 맛있어요"
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data.get('title'), data['title'])
        self.assertEqual(response.data.get('comment'), data['comment'])
        self.assertEqual(response.data.get('user')['id'], self.user.id)
        self.assertEqual(response.data.get('restaurant'), self.restaurant.id)

    def test_get_review_detail(self):
        self.review = Review.objects.create(**self.test_review)
        url = reverse('review-detail', kwargs={'review_id': self.review.id})

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('title'), self.review.title)
        self.assertEqual(response.data.get('comment'), self.review.comment)
        self.assertEqual(response.data.get('user')['id'], self.review.user.id)
        self.assertEqual(response.data.get('restaurant')['id'], self.review.restaurant.id)

    def test_update_review(self):
        self.review = Review.objects.create(**self.test_review)
        url = reverse('review-detail', kwargs={'review_id': self.review.id})
        updated_data = {
            'title': '리뷰 업데이트',
            'comment': '더 맛있어졌어요 ㅎㅎ'
        }

        response = self.client.put(url, updated_data, format='json')

        self.assertEqual(response.status_code, 200)
        self.review.refresh_from_db()
        self.assertEqual(self.review.title, updated_data['title'])
        self.assertEqual(self.review.comment, updated_data['comment'])

    def test_delete_review(self):
        self.review = Review.objects.create(**self.test_review)
        url = reverse('review-detail', kwargs={'review_id': self.review.id})

        response = self.client.delete(url)

        self.assertEqual(response.status_code, 204)
        self.assertFalse(Review.objects.filter(id=self.review.id).exists())
        self.assertEqual(Review.objects.count(), 0)
