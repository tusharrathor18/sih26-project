import api from './api';

export const complianceService = {
  async evaluate(inspectionId) {
    const response = await api.post(`/compliance/inspections/${inspectionId}/evaluate/`);
    return response.data;
  },
  async get(inspectionId) {
    const response = await api.get(`/compliance/inspections/${inspectionId}/compliance/`);
    return response.data;
  },
};
