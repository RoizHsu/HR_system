import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import DashboardView from '../views/DashView.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView
  },
  {
    path: '/dashboard',
    name: 'Employee',
    component: DashboardView,
    meta: { requiresAuth: true }
  } 
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to) => {
  if (!to.meta.requiresAuth) {
    return true
  }

  const token = localStorage.getItem('hr_token')
  if (!token) {
    return '/login'
  }

  const storedEmployee = localStorage.getItem('hr_employee')
  if (!storedEmployee) {
    return '/login'
  }

  try {
    const employee = JSON.parse(storedEmployee)
    if (!employee?.can_manage_employee_data) {
      return '/'
    }
  } catch {
    return '/login'
  }

  return true
})

export default router