import api from './api';

export const scannerService = {
  async listInspections(params = {}) {
    const response = await api.get('/scanner/inspections/history/', { params });
    if (Array.isArray(response.data)) {
      return { results: response.data, next: null, previous: null };
    }
    return response.data;
  },

  async createInspection(productName = '') {
    const response = await api.post('/scanner/inspections/', { product_name: productName });
    return response.data;
  },

  async uploadImage(inspectionId, file, imageType, imageOrder) {
    const body = new FormData();
    body.append('image', file);
    body.append('image_type', imageType);
    body.append('image_order', imageOrder);
    const response = await api.post(`/scanner/inspections/${inspectionId}/images/`, body, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  async processInspection(inspectionId) {
    const response = await api.post(`/scanner/inspections/${inspectionId}/process/`);
    return response.data;
  },

  async getInspection(inspectionId) {
    const response = await api.get(`/scanner/inspections/${inspectionId}/`);
    return response.data;
  },

  async deleteImage(inspectionId, imageId) {
    await api.delete(`/scanner/inspections/${inspectionId}/images/${imageId}/`);
  },

  async verifyInspection(inspectionId, values) {
    const response = await api.patch(`/scanner/inspections/${inspectionId}/verify/`, { values });
    return response.data;
  },

  async getAudit(inspectionId) {
    const response = await api.get(`/scanner/inspections/${inspectionId}/audit/`);
    return response.data;
  },

  async getStats() {
    const response = await api.get('/scanner/dashboard/stats/');
    return response.data;
  },

  async downloadReport(inspectionId) {
    const response = await api.get(`/scanner/inspections/${inspectionId}/report/pdf/`, {
      responseType: 'blob',
    });
    return response.data;
  },
};
