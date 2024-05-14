import { createPinia } from 'pinia'
const store = createPinia()
export { store }
import useCommonStore from './modules/common'
import useUserStore from './modules/user'
import useDatasetStore from './modules/dataset'
import useParagraphStore from './modules/paragraph'
import useModelStore from './modules/model'
import useApplicationStore from './modules/application'
import useDocumentStore from './modules/document'
import useProblemStore from './modules/problem'
import useLogStore from './modules/log'

const useStore = () => ({
  common: useCommonStore(),
  user: useUserStore(),
  dataset: useDatasetStore(),
  paragraph: useParagraphStore(),
  model: useModelStore(),
  application: useApplicationStore(),
  document: useDocumentStore(),
  problem: useProblemStore(),
  log: useLogStore()
})

export default useStore
