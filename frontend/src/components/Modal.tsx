import type { ReactNode } from "react";

interface ModalProps {
  title: string;
  onClose: () => void;
  children: ReactNode;
  headerActions?: ReactNode;
  wide?: boolean;
}

export function Modal({ title, onClose, children, headerActions, wide }: ModalProps) {
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className={wide ? "modal modal-wide" : "modal"} onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{title}</h2>
          <div className="modal-header-actions">
            {headerActions}
            <button type="button" className="modal-close" onClick={onClose} aria-label="Close">
              ×
            </button>
          </div>
        </div>
        <div className="modal-body">{children}</div>
      </div>
    </div>
  );
}

interface DetailRow {
  label: string;
  value: ReactNode;
}

export function DetailGrid({ rows }: { rows: DetailRow[] }) {
  return (
    <dl className="detail-grid">
      {rows.map((row) => (
        <div className="detail-row" key={row.label}>
          <dt>{row.label}</dt>
          <dd>{row.value === "" || row.value === null || row.value === undefined ? "—" : row.value}</dd>
        </div>
      ))}
    </dl>
  );
}
