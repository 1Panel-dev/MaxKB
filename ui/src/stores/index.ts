import { createPinia } from 'pinia'
const store = createPinia()
export { store }
import useUserStore from './modules/user'
import useDatasetStore from './modules/dataset'
import useParagraphStore from './modules/paragraph'

const useStore = () => ({
  user: useUserStore(),
  dataset: useDatasetStore(),
  paragraph:  useParagraphStore(),
})

export default useStore
