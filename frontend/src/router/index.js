import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth.js'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { guest: true }
  },
  {
    path: '/',
    component: () => import('../components/Layout.vue'),
    meta: { requiresAuth: true },
    children: [
      { path: '', name: 'Dashboard', component: () => import('../views/Dashboard.vue') },
      { path: 'categories', name: 'Categories', component: () => import('../views/Categories.vue') },
      { path: 'products', name: 'Products', component: () => import('../views/Products.vue') },
      { path: 'baraban', name: 'Baraban', component: () => import('../views/Baraban.vue') },
      { path: 'users', name: 'Users', component: () => import('../views/Users.vue') },
      { path: 'admins', name: 'Admins', component: () => import('../views/Admins.vue') },
      { path: 'sms', name: 'Sms', component: () => import('../views/Sms.vue') },
      { path: 'operations', name: 'Operations', component: () => import('../views/Operations.vue') },
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  const token = localStorage.getItem('token')

  if (token && !authStore.user && to.meta.requiresAuth) {
    try {
      await authStore.fetchMe()
    } catch {
      next('/login')
      return
    }
  }

  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else if (to.meta.guest && token) {
    next('/')
  } else {
    next()
  }
})

export default router
