import { createRouter, createWebHistory } from 'vue-router'
import { chatRoutes } from './routes'

const chatRouter = createRouter({
  history: createWebHistory(import.meta.env.VITE_BASE_PATH || '/chat/'),
  routes: chatRoutes,
})

chatRouter.afterEach((to) => {
  document.title = to.meta.title ? `${to.meta.title} - MaxKB` : 'MaxKB'
})

export default chatRouter
