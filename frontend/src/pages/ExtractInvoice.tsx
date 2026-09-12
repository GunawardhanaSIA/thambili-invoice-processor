import { useState } from "react";
import { extractInvoiceFields, uploadInvoiceDocument } from "../api/client";
import { DetailGrid } from "../components/Modal";
import type { ExtractedDocument, InvoiceExtraction, InvoiceFields } from "../types";
import { formatAmount } from "../utils/format";

const FIELD_LABELS: { key: keyof InvoiceFields; label: string; amount?: boolean }[] = [
  { key: "supplier_name", label: "Supplier" },
  { key: "invoice_number", label: "Invoice Number" },
  { key: "invoice_date", label: "Invoice Date" },
  { key: "due_date", label: "Due Date" },
  { key: "purchase_order_number", label: "PO Number" },
  { key: "currency", label: "Currency" },
  { key: "subtotal", label: "Subtotal", amount: true },
  { key: "tax_amount", label: "Tax Amount", amount: true },
  { key: "discount_amount", label: "Discount", amount: true },
  { key: "total_amount", label: "Total Amount", amount: true },
];

export function ExtractInvoice() {
  const [file, setFile] = useState<File | null>(null);
  const [document, setDocument] = useState<ExtractedDocument | null>(null);
  const [extraction, setExtraction] = useState<InvoiceExtraction | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleExtract = async () => {
    if (!file) return;

    setLoading(true);
    setError(null);
    setDocument(null);
    setExtraction(null);

    try {
      const doc = await uploadInvoiceDocument(file);
      setDocument(doc);
      const result = await extractInvoiceFields(doc.id);
      setExtraction(result);
    } catch {
      setError("Failed to extract invoice. Check that the backend is running and ANTHROPIC_API_KEY is configured.");
    } finally {
      setLoading(false);
    }
  };

  const currency = (extraction?.fields.currency.value as string) || "";

  return (
    <div>
      <h1>Extract Invoice</h1>
      <p className="page-subtitle">Upload a supplier invoice PDF to extract structured fields with Claude.</p>

      <div className="upload-panel">
        <input
          type="file"
          accept="application/pdf"
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
        />
        <button type="button" className="btn-primary" disabled={!file || loading} onClick={handleExtract}>
          {loading ? "Extracting…" : "Upload & Extract"}
        </button>
      </div>

      {error && <p className="error-text">{error}</p>}

      {document && (
        <div className="extract-section">
          <h2 className="section-title">Document</h2>
          <DetailGrid
            rows={[
              { label: "Filename", value: document.filename },
              { label: "Type", value: document.pdf_type === "scanned" ? "Scanned (OCR)" : "Text" },
              { label: "Pages", value: document.page_count },
            ]}
          />
        </div>
      )}

      {extraction && (
        <div className="extract-section">
          <div className="review-status-row">
            <h2 className="section-title">Extracted Fields</h2>
            <span className={`status-badge status-${extraction.confidence_level.toLowerCase()}`}>
              {extraction.confidence_level} · {(extraction.overall_confidence * 100).toFixed(0)}%
            </span>
            {extraction.requires_review && <span className="review-issue">Needs review</span>}
          </div>

          <DetailGrid
            rows={FIELD_LABELS.map(({ key, label, amount }) => {
              const field = extraction.fields[key];
              const isEmpty = field.value === null || field.value === "";
              const displayValue = isEmpty
                ? null
                : amount
                  ? formatAmount(Number(field.value), currency)
                  : field.value;

              return {
                label,
                value: isEmpty ? null : (
                  <>
                    {displayValue}
                    <span className="field-confidence"> ({(field.confidence * 100).toFixed(0)}%)</span>
                  </>
                ),
              };
            })}
          />

          {extraction.warnings.length > 0 && (
            <ul className="warning-list">
              {extraction.warnings.map((warning) => (
                <li key={warning.code} className={`warning-item warning-${warning.severity.toLowerCase()}`}>
                  {warning.message}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
