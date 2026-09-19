import type { STATE_TYPES } from '@/api/enums'

export type State = (typeof STATE_TYPES)[keyof typeof STATE_TYPES]
