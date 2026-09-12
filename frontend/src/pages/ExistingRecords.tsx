import { useEffect, useState } from "react";
import { fetchExistingRecords } from "../api/client";
import { DetailGrid, Modal } from "../components/Modal";
import { StatusBadge } from "../components/StatusBadge";
import type { ExistingRecord } from "../types";
import { formatAmount } from "../utils/format";

export function ExistingRecords() {
  const [records, setRecords] = useState<ExistingRecord[]>([]);
  const [selected, setSelected] = useState<ExistingRecord | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    fetchExistingRecords()
      .then((data) => {
        if (!cancelled) setRecords(data);
      })
      .catch(() => {
        if (!cancelled) setError("Failed to load existing records.");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div>
      <h1>Existing Records</h1>
      <p className="page-subtitle">Invoice records already entered into the CRM.</p>

      {loading && <p className="empty-state">Loading records…</p>}
      {error && <p className="error-text">{error}</p>}

      {!loading && !error && records.length === 0 && (
        <p className="empty-state">No existing records found.</p>
      )}

      {!loading && !error && records.length > 0 && (
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Record ID</th>
              <th>Supplier ID</th>
              <th>Supplier Name</th>
              <th>Invoice Number</th>
              <th>Date Entered</th>
              <th className="numeric">Net Amount</th>
              <th className="numeric">Tax Amount</th>
              <th className="numeric">Gross Amount</th>
              <th>Status</th>
              <th>Entered By</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {records.map((record) => (
              <tr key={record.record_id}>
                <td className="muted">{record.record_id}</td>
                <td className="muted">{record.supplier_id}</td>
                <td>{record.supplier_name}</td>
                <td>{record.invoice_number}</td>
                <td className="muted">{record.date_entered}</td>
                <td className="numeric">{formatAmount(record.net_amount, record.currency)}</td>
                <td className="numeric">{formatAmount(record.tax_amount, record.currency)}</td>
                <td className="numeric">{formatAmount(record.gross_amount, record.currency)}</td>
                <td>
                  <StatusBadge status={record.status} />
                </td>
                <td className="muted">{record.entered_by}</td>
                <td className="actions-cell">
                  <button type="button" className="btn-view" onClick={() => setSelected(record)}>
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
        <Modal title={`Record ${selected.record_id}`} onClose={() => setSelected(null)}>
          <DetailGrid
            rows={[
              { label: "Record ID", value: selected.record_id },
              { label: "Supplier ID", value: selected.supplier_id },
              { label: "Supplier Name", value: selected.supplier_name },
              { label: "Invoice Number", value: selected.invoice_number },
              { label: "Date Entered", value: selected.date_entered },
              { label: "Net Amount", value: formatAmount(selected.net_amount, selected.currency) },
              { label: "Tax Amount", value: formatAmount(selected.tax_amount, selected.currency) },
              { label: "Gross Amount", value: formatAmount(selected.gross_amount, selected.currency) },
              { label: "Status", value: <StatusBadge status={selected.status} /> },
              { label: "Entered By", value: selected.entered_by },
              { label: "Currency", value: selected.currency },
              { label: "Cost Centre", value: selected.cost_centre },
            ]}
          />
        </Modal>
      )}
    </div>
  );
}
