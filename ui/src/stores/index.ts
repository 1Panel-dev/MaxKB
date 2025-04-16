import useLoginStore from './modules/login'
import useUserStore from './modules/user'

const useStore = () => ({
  login: useLoginStore(),
  user: useUserStore(),
})

export default useStore
