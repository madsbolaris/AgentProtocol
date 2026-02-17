import React from 'react'
import { useUIStore, type Notification } from '../../store/useUIStore'

function NotificationToast({ notification }: { notification: Notification }) {
  const removeNotification = useUIStore((s) => s.removeNotification)

  const getIcon = () => {
    switch (notification.type) {
      case 'success':
        return '✓'
      case 'error':
        return '✗'
      case 'warning':
        return '⚠'
      case 'info':
        return 'ℹ'
    }
  }

  return (
    <div className={`notification-toast notification-${notification.type}`}>
      <div className="notification-content">
        <span className="notification-icon">{getIcon()}</span>
        <span className="notification-message">{notification.message}</span>
      </div>
      <button
        className="notification-close"
        onClick={() => removeNotification(notification.id)}
        aria-label="Close notification"
      >
        ×
      </button>
    </div>
  )
}

export function NotificationCenter() {
  const notifications = useUIStore((s) => s.notifications)

  if (notifications.length === 0) return null

  return (
    <div className="notification-center">
      {notifications.map((notification) => (
        <NotificationToast key={notification.id} notification={notification} />
      ))}
    </div>
  )
}
