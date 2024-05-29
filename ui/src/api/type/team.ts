interface TeamMember {
  id: string
  username: string
  email: string
  team_id: string
  /**
   * 類型：type：manage 所有者；
   */
  type: string
  user_id: string
}

export type { TeamMember }
