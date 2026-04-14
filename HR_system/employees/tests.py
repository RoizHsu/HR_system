from django.contrib.auth.models import Group, User
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from .models import Employee


class EmployeePermissionTests(APITestCase):
	def setUp(self):
		self.hr_group = Group.objects.create(name='人資群組')

		self.normal_user = User.objects.create_user(username='normal', password='pass12345')
		self.hr_user = User.objects.create_user(username='hr', password='pass12345')
		self.hr_user.groups.add(self.hr_group)

		self.normal_employee = Employee.objects.create(
			user=self.normal_user,
			employee_id='EMP0001',
			account='normal',
			email='normal@example.com',
			name='一般員工',
		)
		self.hr_employee = Employee.objects.create(
			user=self.hr_user,
			employee_id='EMP0002',
			account='hr',
			email='hr@example.com',
			name='人資員工',
		)

		self.normal_token = Token.objects.create(user=self.normal_user)
		self.hr_token = Token.objects.create(user=self.hr_user)

	def _auth_with_token(self, token):
		self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

	def test_normal_user_cannot_update_self(self):
		self._auth_with_token(self.normal_token)
		response = self.client.patch('/api/employees/list/me/update/', {'name': '新名字'}, format='json')
		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

	def test_hr_user_can_update_self(self):
		self._auth_with_token(self.hr_token)
		response = self.client.patch('/api/employees/list/me/update/', {'name': '人資新名字'}, format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.hr_employee.refresh_from_db()
		self.assertEqual(self.hr_employee.name, '人資新名字')

	def test_normal_user_list_only_sees_self(self):
		self._auth_with_token(self.normal_token)
		response = self.client.get('/api/employees/list/')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(len(response.data), 1)
		self.assertEqual(response.data[0]['id'], self.normal_employee.id)

	def test_hr_user_list_sees_all_employees(self):
		self._auth_with_token(self.hr_token)
		response = self.client.get('/api/employees/list/')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(len(response.data), 2)

	def test_normal_user_cannot_update_other_employee(self):
		self._auth_with_token(self.normal_token)
		response = self.client.patch(
			f'/api/employees/list/{self.hr_employee.id}/',
			{'name': '試圖修改'},
			format='json',
		)
		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

	def test_editor_cannot_update_disallowed_fields(self):
		self._auth_with_token(self.hr_token)
		response = self.client.patch(
			f'/api/employees/list/{self.normal_employee.id}/',
			{'user': self.hr_user.id},
			format='json',
		)
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_company_edit_access_flag(self):
		self._auth_with_token(self.normal_token)
		normal_response = self.client.get('/api/employees/list/company-edit-access/')
		self.assertEqual(normal_response.status_code, status.HTTP_200_OK)
		self.assertFalse(normal_response.data['can_manage_employee_data'])

		self._auth_with_token(self.hr_token)
		hr_response = self.client.get('/api/employees/list/company-edit-access/')
		self.assertEqual(hr_response.status_code, status.HTTP_200_OK)
		self.assertTrue(hr_response.data['can_manage_employee_data'])

	def test_login_response_returns_correct_group_permission_flag(self):
		self.client.credentials()
		response = self.client.post(
			'/api/employees/auth/login/',
			{'account': 'hr', 'password': 'pass12345'},
			format='json',
		)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertTrue(response.data['employee']['can_manage_employee_data'])
