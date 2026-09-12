import axios from "axios";
import { mockExistingRecords, mockReviewInvoices, mockSuppliers } from "../data/mockData";
import type { ExistingRecord, ReviewInvoice, Supplier } from "../types";

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "http://localhost:8000/api",
});

export async function fetchReviewInvoices(): Promise<ReviewInvoice[]> {
  try {
    const { data } = await apiClient.get<ReviewInvoice[]>("/invoices");
    return data;
  } catch {
    return mockReviewInvoices;
  }
}

export async function fetchSuppliers(): Promise<Supplier[]> {
  try {
    const { data } = await apiClient.get<Supplier[]>("/suppliers");
    return data;
  } catch {
    return mockSuppliers;
  }
}

export async function fetchExistingRecords(): Promise<ExistingRecord[]> {
  try {
    const { data } = await apiClient.get<ExistingRecord[]>("/records");
    return data;
  } catch {
    return mockExistingRecords;
  }
}
