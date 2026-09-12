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

export interface ExtractedDocument {
  id: string;
  filename: string;
  pdf_type: string;
  page_count: number;
  extracted_text: string;
  created_at: string;
}

export interface AIField {
  value: string | number | null;
  confidence: number;
  evidence: string | null;
}

export interface InvoiceFields {
  supplier_name: AIField;
  invoice_number: AIField;
  invoice_date: AIField;
  due_date: AIField;
  purchase_order_number: AIField;
  currency: AIField;
  subtotal: AIField;
  tax_amount: AIField;
  discount_amount: AIField;
  total_amount: AIField;
}

export interface AIWarning {
  code: string;
  message: string;
  severity: string;
  field?: string | null;
}

export interface InvoiceExtraction {
  id: string;
  document_id: string;
  success: boolean;
  fields: InvoiceFields;
  overall_confidence: number;
  confidence_level: "HIGH" | "MEDIUM" | "LOW";
  requires_review: boolean;
  warnings: AIWarning[];
  error?: string | null;
  created_at: string;
}
