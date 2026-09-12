# Sample data

Local-only sample dataset for manual testing and development. Not committed
to git (see the root `.gitignore`) — copy it in from the challenge dataset
whenever you need it locally.

- `suppliers.csv` — sample rows matching `app.schemas.supplier.Supplier`
- `existing_records.csv` — sample rows matching `app.schemas.record.ExistingRecord`
- `invoices/` — sample supplier invoice PDFs (text-based and scanned) for
  testing `POST /api/documents/extract` and `POST /api/documents/{id}/extract-invoice`
