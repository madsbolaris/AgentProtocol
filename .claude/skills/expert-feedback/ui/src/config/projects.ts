/**
 * Project configuration for project selector dropdown
 */

export interface ProjectConfig {
  id: string
  name: string
  badgeCount?: number
}

export const projects: ProjectConfig[] = [
  {
    id: 'ux-update-review',
    name: 'UX Update Review',
    badgeCount: 7
  },
  {
    id: 'backend-review',
    name: 'Backend Review',
    badgeCount: 3
  },
  {
    id: 'api-design-review',
    name: 'API Design Review',
    badgeCount: 2
  },
  {
    id: 'security-audit',
    name: 'Security Audit'
  }
]
