import useLoginStore from './modules/login'
import useUserStore from './modules/user'
import useFolderStore from './modules/folder'

const useStore = () => ({
  login: useLoginStore(),
  user: useUserStore(),
  folder: useFolderStore(),
})

export default useStore
