import api from './api';

export const authService = {
  /**
   * Authenticate officer via Officer ID and password
   */
  async login(officer_id, password) {
    const response = await api.post('/users/login/', {
      officer_id: officer_id.trim(),
      password: password,
    });
    return response.data;
  },

  /**
   * Fetch current authenticated officer's profile
   */
  async getProfile() {
    const response = await api.get('/users/me/');
    return response.data;
  },

  /**
   * Logout officer and invalidate token on backend
   */
  async logout() {
    try {
      await api.post('/users/logout/');
    } catch (e) {
      console.warn('Backend logout encountered error, clearing client credentials locally:', e);
    } finally {
      localStorage.removeItem('officer_token');
      localStorage.removeItem('officer_data');
    }
  },

  /**
   * Health check endpoint
   */
  async checkHealth() {
    const response = await api.get('/health/');
    return response.data;
  },
};
