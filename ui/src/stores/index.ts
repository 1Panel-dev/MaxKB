import { createPinia } from 'pinia'
const store = createPinia()
export { store }
import useUserStore from './modules/user'

const useStore = () => ({
  user: useUserStore()
})

export default useStore
