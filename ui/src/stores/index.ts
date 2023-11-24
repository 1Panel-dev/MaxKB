import { createPinia } from 'pinia'
const store = createPinia()
export { store }
import useCommonStore from './modules/common'
import useUserStore from './modules/user'
import useDatasetStore from './modules/dataset'
import useParagraphStore from './modules/paragraph'
import useModelStore from './modules/model'
import useApplicationStore from './modules/application'

const useStore = () => ({
  common: useCommonStore(),
  user: useUserStore(),
  dataset: useDatasetStore(),
  paragraph: useParagraphStore(),
  model: useModelStore(),
  application: useApplicationStore()
})

export default useStore
