import api from './api';

export const scannerService = {
  async listInspections() {
    const response = await api.get('/scanner/inspections/');
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
};
