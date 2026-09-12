export type ReviewStatus = "Pending Review" | "Needs Attention" | "Approved" | "Rejected";

export interface ReviewInvoice {
  id: string;
  supplier_id: string;
  supplier_name: string;
  invoice_number: string;
  net_amount: number;
  tax_amount: number;
  gross_amount: number;
  cost_centre: string;
  status: ReviewStatus;
  issue: string;
  currency: string;
  document_url?: string;
}

export interface Supplier {
  supplier_id: string;
  registered_name: string;
  trading_name: string;
  category: string;
  address: string;
  city: string;
  phone: string;
  email: string;
  vat_number: string;
  payment_terms: string;
  currency: string;
}

export interface ExistingRecord {
  record_id: string;
  supplier_id: string;
  supplier_name: string;
  invoice_number: string;
  date_entered: string;
  net_amount: number;
  tax_amount: number;
  gross_amount: number;
  status: string;
  entered_by: string;
  currency: string;
  cost_centre: string;
}
