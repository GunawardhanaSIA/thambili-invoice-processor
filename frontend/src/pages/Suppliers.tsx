import { useEffect, useState } from "react";
import { fetchSuppliers } from "../api/client";
import { DetailGrid, Modal } from "../components/Modal";
import type { Supplier } from "../types";

export function Suppliers() {
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [selected, setSelected] = useState<Supplier | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    fetchSuppliers()
      .then((data) => {
        if (!cancelled) setSuppliers(data);
      })
      .catch(() => {
        if (!cancelled) setError("Failed to load suppliers.");
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
      <h1>Suppliers</h1>
      <p className="page-subtitle">Thambili's registered suppliers.</p>

      {loading && <p className="empty-state">Loading suppliers…</p>}
      {error && <p className="error-text">{error}</p>}

      {!loading && !error && suppliers.length === 0 && (
        <p className="empty-state">No suppliers found.</p>
      )}

      {!loading && !error && suppliers.length > 0 && (
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Supplier ID</th>
              <th>Registered Name</th>
              <th>Trading Name</th>
              <th>Category</th>
              <th>Address</th>
              <th>City</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {suppliers.map((supplier) => (
              <tr key={supplier.supplier_id}>
                <td className="muted">{supplier.supplier_id}</td>
                <td>{supplier.registered_name}</td>
                <td>{supplier.trading_name}</td>
                <td className="muted">{supplier.category}</td>
                <td className="muted">{supplier.address}</td>
                <td className="muted">{supplier.city}</td>
                <td className="actions-cell">
                  <button type="button" className="btn-view" onClick={() => setSelected(supplier)}>
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
        <Modal title={selected.registered_name} onClose={() => setSelected(null)}>
          <DetailGrid
            rows={[
              { label: "Supplier ID", value: selected.supplier_id },
              { label: "Registered Name", value: selected.registered_name },
              { label: "Trading Name", value: selected.trading_name },
              { label: "Category", value: selected.category },
              { label: "Address", value: selected.address },
              { label: "City", value: selected.city },
              { label: "Phone", value: selected.phone },
              { label: "Email", value: selected.email },
              { label: "VAT Number", value: selected.vat_number },
              { label: "Payment Terms", value: selected.payment_terms },
              { label: "Currency", value: selected.currency },
            ]}
          />
        </Modal>
      )}
    </div>
  );
}
