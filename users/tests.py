from django.contrib.auth.hashers import check_password
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class UserModelTest(TestCase):
    def setUp(self):
        self.test_user = {
            'email': 'test@example.com',
            'nickname': 'testuser',
            'password': 'password1234',
        }

        self.test_admin_user = {
            'email': 'admin@example.com',
            'nickname': 'adminuser',
            'password': 'password1234',
        }

    def test_user_manager_create_user(self):
        # 유저 매니저를 사용하여 setUp 데이터를 바탕으로 유저 모델을 생성
        user = User.objects.create_user(**self.test_user)

        # 유저 모델이 생성되었는지 카운트를 확인
        self.assertEqual(User.objects.all().count(), 1)

        # 생성된 유저 모델의 속성을 확인
        self.assertEqual(user.email, self.test_user['email'])
        self.assertEqual(user.nickname, self.test_user['nickname'])
        self.assertTrue(user.check_password(self.test_user['password']))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_active)
        # 프로필 이미지는 따로 넣지 않았기 때문에 디폴트 이미지인지 확인
        self.assertEqual(user.profile_image.url, '/media/users/blank_profile_image.jpg')

    def test_user_manager_create_superuser(self):
        # 관리자 권한을 가진 유저 모델을 생성
        admin_user = User.objects.create_superuser(**self.test_admin_user)

        # 어드민 유저 모델이 생성되었는지 카운트를 확인
        self.assertEqual(User.objects.filter(is_superuser=True, is_staff=True).count(), 1)
        self.assertEqual(admin_user.email, self.test_admin_user['email'])
        self.assertEqual(admin_user.nickname, self.test_admin_user['nickname'])
        self.assertTrue(admin_user.check_password(self.test_admin_user['password']))
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        self.assertTrue(admin_user.is_active)
        # 프로필 이미지는 따로 넣지 않았기 때문에 디폴트 이미지인지 확인
        self.assertEqual(admin_user.profile_image.url, '/media/users/blank_profile_image.jpg')


class UserAPITestCase(APITestCase):
    def setUp(self):
        self.data = {
            'nickname': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword1234'
        }

    def test_user_signup(self):
        response = self.client.post(reverse('user-signup'), self.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(response.data.get('nickname'), 'testuser')
        self.assertEqual(response.data.get('email'), 'test@example.com')

    def test_user_login(self):
        user = User.objects.create_user(**self.data)
        data = {
            'email': user.email,
            'password': 'testpassword1234'
        }

        response = self.client.post(reverse('user-login'), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertEqual(response.data.get('message'), 'login successful.')

    def test_user_login_invalid_credentials(self):
        data = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }
        response = self.client.post(reverse('user-login'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_user_details(self):
        user = User.objects.create_user(**self.data)
        self.client.login(email='test@example.com', password='testpassword1234')

        response = self.client.get(reverse('user-detail', kwargs={'pk': user.id}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('nickname'), 'testuser')
        self.assertEqual(response.data.get('email'), 'test@example.com')

    def test_update_user_details(self):
        user = User.objects.create_user(**self.data)
        self.client.login(email='test@example.com', password='testpassword1234')
        data = {
            'nickname': 'updateduser',
            'password': 'updatepw1234'
        }

        response = self.client.patch(reverse('user-detail', kwargs={'pk': user.id}), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('nickname'), 'updateduser')
        # 요청으로 인한 변경사항을 db로 부터 가져옴
        user.refresh_from_db()
        self.assertTrue(check_password('updatepw1234', user.password))

    def test_delete_user(self):
        user = User.objects.create_user(**self.data)
        self.client.login(email='test@example.com', password='testpassword1234')

        response = self.client.delete(reverse('user-detail', kwargs={'pk': user.id}))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(email='test@example.com').exists())

    def test_jwt_login(self):
        user = User.objects.create_user(**self.data)
        data = {
            'email': user.email,
            'password': 'testpassword1234'
        }

        response = self.client.post(reverse('jwt-login'), data)
        last_login = user.last_login
        user.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertNotEqual(user.last_login, last_login)

    def test_jwt_verify(self):
        user = User.objects.create_user(**self.data)
        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)

        response = self.client.post(
            path=reverse('token-verify'),
            data={'token': access},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_jwt_refresh(self):
        user = User.objects.create_user(**self.data)
        refresh = RefreshToken.for_user(user)

        response = self.client.post(
            path=reverse('token-refresh'),
            data={'refresh': str(refresh)}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)