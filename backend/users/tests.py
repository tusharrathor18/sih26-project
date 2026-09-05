import os
import secrets
from unittest.mock import patch

from django.core.management import call_command, CommandError
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from users.models import OfficerProfile

class OfficerAuthApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create active test officer
        self.active_user = User.objects.create_user(
            username='test_inspector',
            email='test.inspector@delhi.gov.in',
            password='TestPassword@123',
            is_active=True
        )
        self.active_profile = OfficerProfile.objects.create(
            user=self.active_user,
            officer_id='OFF-TEST-001',
            name='Test Inspector Kumar',
            designation='Legal Metrology Inspector',
            department='Department of Consumer Affairs',
            jurisdiction='Zone-1, North Delhi',
            role='INSPECTOR',
            is_active=True
        )

        # Create inactive test officer
        self.inactive_user = User.objects.create_user(
            username='test_inactive',
            email='inactive.officer@delhi.gov.in',
            password='TestPassword@123',
            is_active=True
        )
        self.inactive_profile = OfficerProfile.objects.create(
            user=self.inactive_user,
            officer_id='OFF-INACT-001',
            name='Inactive Officer',
            designation='Suspended Inspector',
            department='Department of Consumer Affairs',
            jurisdiction='Zone-2',
            role='INSPECTOR',
            is_active=False
        )

    def test_health_check_endpoint(self):
        """Verify public health API returns 200 and expected payload"""
        response = self.client.get('/api/health/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'ok')
        self.assertEqual(response.data['message'], 'Legal Metrology API is running')

    def test_successful_officer_login(self):
        """Verify active officer can log in via /api/auth/login/"""
        payload = {
            'officer_id': 'OFF-TEST-001',
            'password': 'TestPassword@123'
        }
        response = self.client.post('/api/auth/login/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('token', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['officer_id'], 'OFF-TEST-001')
        self.assertEqual(response.data['user']['name'], 'Test Inspector Kumar')
        self.assertNotIn('password', response.data)
        self.assertNotIn('password', response.data['user'])
        self.assertNotIn('password', response.data['officer'])
        self.assertNotIn(self.active_user.password, str(response.data))

    def test_login_invalid_password(self):
        """Verify login fails with wrong password"""
        payload = {
            'officer_id': 'OFF-TEST-001',
            'password': 'WrongPassword@999'
        }
        response = self.client.post('/api/auth/login/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(response.data['success'])

    def test_login_nonexistent_officer(self):
        """Verify login fails when officer does not exist"""
        payload = {
            'officer_id': 'OFF-NONEXISTENT',
            'password': 'AnyPassword@123'
        }
        response = self.client.post('/api/auth/login/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(response.data['success'])

    def test_login_inactive_officer(self):
        """Verify inactive officer cannot log in"""
        payload = {
            'officer_id': 'OFF-INACT-001',
            'password': 'TestPassword@123'
        }
        response = self.client.post('/api/auth/login/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(response.data['success'])
        self.assertIn('inactive', response.data['message'].lower())

    def test_get_current_officer_authenticated(self):
        """Verify /api/auth/me/ returns officer details for authenticated token"""
        login_res = self.client.post('/api/auth/login/', {
            'officer_id': 'OFF-TEST-001',
            'password': 'TestPassword@123'
        }, format='json')
        token = login_res.data['token']

        # Call /api/auth/me/ with Token
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        me_res = self.client.get('/api/auth/me/')
        self.assertEqual(me_res.status_code, status.HTTP_200_OK)
        self.assertEqual(me_res.data['officer_id'], 'OFF-TEST-001')
        self.assertEqual(me_res.data['name'], 'Test Inspector Kumar')

    def test_get_current_officer_unauthenticated(self):
        """Verify /api/auth/me/ returns 401 when no token is provided"""
        response = self.client.get('/api/auth/me/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_officer_logout(self):
        """Verify /api/auth/logout/ invalidates token"""
        login_res = self.client.post('/api/auth/login/', {
            'officer_id': 'OFF-TEST-001',
            'password': 'TestPassword@123'
        }, format='json')
        token = login_res.data['token']

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        logout_res = self.client.post('/api/auth/logout/')
        self.assertEqual(logout_res.status_code, status.HTTP_200_OK)

        # Subsequent call with same token must now fail
        me_res = self.client.get('/api/auth/me/')
        self.assertEqual(me_res.status_code, status.HTTP_401_UNAUTHORIZED)


class SeedOfficerSecurityTests(TestCase):
    password_variables = {
        f"OFFICER_{index:02d}_PASSWORD": secrets.token_urlsafe(24)
        for index in range(1, 5)
    }

    def test_seed_fails_when_an_officer_password_is_missing(self):
        with patch.dict(os.environ, self.password_variables, clear=False):
            os.environ.pop("OFFICER_02_PASSWORD", None)
            with self.assertRaises(CommandError) as context:
                call_command("seed_officers")

        self.assertIn("OFFICER_02_PASSWORD", str(context.exception))
        self.assertFalse(User.objects.filter(username="admin_officer").exists())

    def test_seed_hashes_new_password_and_does_not_reset_existing_password(self):
        with patch.dict(os.environ, self.password_variables, clear=False):
            call_command("seed_officers", verbosity=0)

            user = User.objects.get(username="admin_officer")
            first_hash = user.password
            self.assertTrue(user.check_password(self.password_variables["OFFICER_01_PASSWORD"]))
            self.assertNotEqual(first_hash, self.password_variables["OFFICER_01_PASSWORD"])

            replacement_values = {
                key: secrets.token_urlsafe(24)
                for key in self.password_variables
            }
            with patch.dict(os.environ, replacement_values, clear=False):
                call_command("seed_officers", verbosity=0)

            user.refresh_from_db()
            self.assertEqual(user.password, first_hash)
            self.assertTrue(user.check_password(self.password_variables["OFFICER_01_PASSWORD"]))
