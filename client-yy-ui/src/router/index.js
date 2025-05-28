import { createRouter, createWebHashHistory } from 'vue-router'
import http from '../utils/http'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: '/', redirect: '/main' },
    { path: '/login', component: () => import('../views/Login.vue') },
    { path: '/main', component: () => import('../views/Main.vue') },
  ],
})

router.beforeEach(async (to, form, next) => {
  if (to.path !== '/login') {
    const res = await http.post('/client/check')
    if (res.data.success) {
      return next()
    } else {
      return next('/login')
    }
  } else {
    return next()
  }
})

export default router
