import { createPinia } from 'pinia'
const store = createPinia()
export { store }
import useUserStore from './modules/user'
import useDatasetStore from './modules/dataset'
import useParagraphStore from './modules/paragraph'
import useModelStore from './modules/model'

const useStore = () => ({
  user: useUserStore(),
  dataset: useDatasetStore(),
  paragraph:  useParagraphStore(),
  model:  useModelStore(),
})

export default useStore
