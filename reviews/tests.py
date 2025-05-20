from django.contrib.auth import get_user_model
from django.test import TestCase

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