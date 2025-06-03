import axios from "axios";

const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Users API
export const usersAPI = {
  create: (userData) => api.post("/users/", userData),
  get: (userId) => api.get(`/users/${userId}`),
};

// Projects API
export const projectsAPI = {
  create: (projectData, ownerId) =>
    api.post(`/projects/?owner_id=${ownerId}`, projectData),
  get: (projectId) => api.get(`/projects/${projectId}`),
};

// Tasks API
export const tasksAPI = {
  create: (taskData, projectId) =>
    api.post(`/tasks/?project_id=${projectId}`, taskData),
  get: (taskId) => api.get(`/tasks/${taskId}`),
};

// Goals API
export const goalsAPI = {
  create: (goalData, projectId) =>
    api.post(`/goals/?project_id=${projectId}`, goalData),
  get: (goalId) => api.get(`/goals/${goalId}`),
};

export default api;
