// Notification Service integrating Frontend UI with real Backend API endpoints

import { apiRequest } from './api';

export const notificationService = {
  getNotifications: async (limit = 50) => {
    try {
      const res = await apiRequest(`/notifications?limit=${limit}`);
      return Array.isArray(res) ? res : [];
    } catch (e) {
      console.warn('Backend unavailable for getNotifications', e);
      return [];
    }
  },

  getUnreadCount: async () => {
    try {
      const res = await apiRequest('/notifications/count');
      return res?.unread_count || 0;
    } catch (e) {
      return 0;
    }
  },

  markAsRead: async (notificationId) => {
    try {
      return await apiRequest(`/notifications/${notificationId}/read`, { method: 'PATCH' });
    } catch (e) {
      return null;
    }
  },

  markAllAsRead: async () => {
    try {
      return await apiRequest('/notifications/read-all', { method: 'POST' });
    } catch (e) {
      return null;
    }
  },

  deleteNotification: async (notificationId) => {
    try {
      return await apiRequest(`/notifications/${notificationId}`, { method: 'DELETE' });
    } catch (e) {
      return null;
    }
  },

  getPreferences: async () => {
    try {
      return await apiRequest('/notifications/preferences');
    } catch (e) {
      return {
        task_reminders: true,
        achievement_notifications: true,
        roadmap_notifications: true,
        interview_notifications: true,
        general_notifications: true
      };
    }
  },

  updatePreferences: async (preferences) => {
    try {
      return await apiRequest('/notifications/preferences', {
        method: 'PUT',
        body: JSON.stringify(preferences)
      });
    } catch (e) {
      return preferences;
    }
  }
};
