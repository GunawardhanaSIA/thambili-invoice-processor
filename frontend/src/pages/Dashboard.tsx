import { useEffect, useState } from "react";
import { approveInvoice, fetchReviewInvoices } from "../api/client";
import { Modal } from "../components/Modal";
import { StatusBadge } from "../components/StatusBadge";
import type { ReviewInvoice } from "../types";
import { formatAmount } from "../utils/format";

const COMPARE_FIELDS: { key: keyof ReviewInvoice; label: string }[] = [
  { key: "supplier_id", label: "Supplier ID" },
  { key: "supplier_name", label: "Supplier Name" },
  { key: "invoice_number", label: "Invoice Number" },
  { key: "currency", label: "Currency" },
];

function ReviewModal({
  invoice,
  onClose,
  onApprove,
}: {
  invoice: ReviewInvoice;
  onClose: () => void;
  onApprove: (updated: ReviewInvoice) => void;
}) {
  const [draft, setDraft] = useState<ReviewInvoice>(invoice);
  const [editableFields] = useState<Set<string>>(
    () => new Set(COMPARE_FIELDS.filter(({ key }) => !invoice[key]).map(({ key }) => key)),
  );

  const handleFieldChange = (key: keyof ReviewInvoice, value: string) => {
    setDraft((prev) => ({ ...prev, [key]: value }));
  };

  return (
    <Modal
      title={`Invoice ${invoice.invoice_number}`}
      onClose={onClose}
      wide
      headerActions={
        <button type="button" className="btn-approve" onClick={() => onApprove(draft)}>
          Approve
        </button>
      }
    >
      <div className="review-split">
        <div className="review-doc-panel">
          {draft.document_url ? (
            <iframe src={draft.document_url} title={`Source document for ${draft.invoice_number}`} />
          ) : (
            <div className="review-doc-placeholder">
              <p>No source document available for preview.</p>
              <p className="muted-small">The original invoice PDF will appear here once uploaded.</p>
            </div>
          )}
        </div>

        <div className="review-fields-panel">
          <div className="review-status-row">
            <StatusBadge status={draft.status} />
            {draft.issue && <span className="review-issue">{draft.issue}</span>}
          </div>

          <dl className="detail-grid">
            {COMPARE_FIELDS.map(({ key, label }) => {
              const value = draft[key] as string;
              const isEmpty = !value;
              const isEditable = editableFields.has(key);
              return (
                <div className={isEmpty ? "detail-row detail-row-missing" : "detail-row"} key={key}>
                  <dt>{label}</dt>
                  <dd>
                    {isEditable ? (
                      <input
                        type="text"
                        className="field-input"
                        placeholder="Enter from document"
                        value={value ?? ""}
                        onChange={(e) => handleFieldChange(key, e.target.value)}
                      />
                    ) : (
                      value
                    )}
                  </dd>
                </div>
              );
            })}
            <div className="detail-row">
              <dt>Net Amount</dt>
              <dd>{formatAmount(draft.net_amount, draft.currency)}</dd>
            </div>
            <div className="detail-row">
              <dt>Tax Amount</dt>
              <dd>{formatAmount(draft.tax_amount, draft.currency)}</dd>
            </div>
            <div className="detail-row">
              <dt>Gross Amount</dt>
              <dd>{formatAmount(draft.gross_amount, draft.currency)}</dd>
            </div>
          </dl>
        </div>
      </div>
    </Modal>
  );
}

export function Dashboard() {
  const [invoices, setInvoices] = useState<ReviewInvoice[]>([]);
  const [selected, setSelected] = useState<ReviewInvoice | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    fetchReviewInvoices()
      .then((data) => {
        if (!cancelled) setInvoices(data);
      })
      .catch(() => {
        if (!cancelled) setError("Failed to load invoices for review.");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const handleApprove = async (updated: ReviewInvoice) => {
    try {
      const approved = await approveInvoice(updated);
      setInvoices((prev) => prev.filter((invoice) => invoice.id !== approved.id));
      setSelected(null);
    } catch {
      setError("Failed to approve invoice. Please try again.");
    }
  };

  return (
    <div>
      <h1>Review Queue</h1>
      <p className="page-subtitle">Invoices extracted from supplier PDFs, awaiting review and approval.</p>

      {loading && <p className="empty-state">Loading invoices…</p>}
      {error && <p className="error-text">{error}</p>}

      {!loading && !error && invoices.length === 0 && (
        <p className="empty-state">No invoices are waiting for review.</p>
      )}

      {!loading && !error && invoices.length > 0 && (
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Supplier ID</th>
              <th>Supplier Name</th>
              <th>Invoice Number</th>
              <th className="numeric">Net Amount</th>
              <th className="numeric">Tax Amount</th>
              <th className="numeric">Gross Amount</th>
              <th>Status</th>
              <th>Issue</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {invoices.map((invoice) => (
              <tr key={invoice.id}>
                <td className="muted">{invoice.supplier_id}</td>
                <td>{invoice.supplier_name}</td>
                <td>{invoice.invoice_number}</td>
                <td className="numeric">{formatAmount(invoice.net_amount, invoice.currency)}</td>
                <td className="numeric">{formatAmount(invoice.tax_amount, invoice.currency)}</td>
                <td className="numeric">{formatAmount(invoice.gross_amount, invoice.currency)}</td>
                <td>
                  <StatusBadge status={invoice.status} />
                </td>
                <td className="muted">{invoice.issue || "—"}</td>
                <td className="actions-cell">
                  <button type="button" className="btn-view" onClick={() => setSelected(invoice)}>
                    View more
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      )}

      {selected && (
        <ReviewModal invoice={selected} onClose={() => setSelected(null)} onApprove={handleApprove} />
      )}
    </div>
  );
}
