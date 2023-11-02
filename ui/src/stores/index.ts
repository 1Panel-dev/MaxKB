import { createPinia } from 'pinia'
const store = createPinia()
export { store }
import useUserStore from './modules/user'
import useDatasetStore from './modules/dataset'

const useStore = () => ({
  user: useUserStore(),
  dataset: useDatasetStore()
})

export default useStore
