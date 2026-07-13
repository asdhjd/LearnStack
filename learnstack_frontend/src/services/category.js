import axios from 'axios';
import { API_BASE_URL } from '@/config/api';

const BASE_URL = `${API_BASE_URL}/categories`;

export const getParentCategories = async () => {
  return axios.get(`${BASE_URL}/`);
};

export const getHotSubcategories = async () => {
  return axios.get(`${BASE_URL}/hotsubcategories`);
};

export const getCategories = async () => {
  const response = await axios.get(`${BASE_URL}/AllList`);
  return response.data;
};

export const getAllTechnologies = async () => {
  const response = await axios.get(`${BASE_URL}/allTechnologies`);
  return response.data;
};

export const getCategoryDetail = async (id) => {
  const response = await axios.get(`${BASE_URL}/${id}/`);
  return response;
};