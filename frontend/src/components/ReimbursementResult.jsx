function ReimbursementResult({ result }) {
  if (!result) return null;

  const getStatusClass = (status) => {
    switch (status) {
      case 'approved':
        return 'status-approved';
      case 'rejected':
        return 'status-rejected';
      case 'pending_review':
        return 'status-pending';
      case 'processing':
        return 'status-processing';
      default:
        return '';
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString();
  };

  const formatCurrency = (amount, currency) => {
    if (!amount) return 'N/A';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency || 'USD',
    }).format(amount);
  };

  return (
    <div className="result-card">
      <h3>Reimbursement Result</h3>
      
      <div className="result-item">
        <label>Status:</label>
        <span className={getStatusClass(result.status)}>
          {result.status.toUpperCase()}
        </span>
      </div>

      <div className="result-item">
        <label>Employee:</label>
        <span>{result.employee_name} ({result.employee_employee_id})</span>
      </div>

      <div className="result-item">
        <label>Category:</label>
        <span>
          {result.category_name || (
            <span style={{ color: '#e67e22', fontStyle: 'italic' }}>
              Not determined (pending review)
            </span>
          )}
        </span>
      </div>

      <div className="result-item">
        <label>Amount:</label>
        <span>{formatCurrency(result.amount, result.currency)}</span>
      </div>

      {result.remaining_balance !== null && (
        <div className="result-item">
          <label>Remaining Balance:</label>
          <span>{formatCurrency(result.remaining_balance, result.currency)}</span>
        </div>
      )}

      <div className="result-item">
        <label>Submission Date:</label>
        <span>{formatDate(result.submission_timestamp)}</span>
      </div>

      {result.rejection_reason && (
        <div className="result-item">
          <label>Rejection Reason:</label>
          <span style={{ color: '#e74c3c' }}>{result.rejection_reason}</span>
        </div>
      )}

      {result.invoice && (
        <div style={{ marginTop: '20px', paddingTop: '20px', borderTop: '1px solid #eee' }}>
          <h4 style={{ marginBottom: '12px' }}>Invoice Details</h4>
          
          {result.invoice.vendor_name && (
            <div className="result-item">
              <label>Vendor:</label>
              <span>{result.invoice.vendor_name}</span>
            </div>
          )}

          {result.invoice.purchase_date && (
            <div className="result-item">
              <label>Purchase Date:</label>
              <span>{new Date(result.invoice.purchase_date).toLocaleDateString()}</span>
            </div>
          )}

          {result.invoice.invoice_number && (
            <div className="result-item">
              <label>Invoice Number:</label>
              <span>{result.invoice.invoice_number}</span>
            </div>
          )}

          {result.invoice.items && result.invoice.items.length > 0 && (
            <div className="result-item">
              <label>Items:</label>
              <div style={{ marginTop: '8px' }}>
                {result.invoice.items.map((item, index) => (
                  <div key={index} style={{ marginBottom: '4px', fontSize: '14px' }}>
                    - {item.description}
                    {item.amount && ` (${formatCurrency(item.amount, result.invoice.currency)})`}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {result.cloudinary_url && (
        <div style={{ marginTop: '20px' }}>
          <a
            href={result.cloudinary_url}
            target="_blank"
            rel="noopener noreferrer"
            style={{ color: '#3498db', textDecoration: 'none' }}
          >
            View Invoice Image →
          </a>
        </div>
      )}
    </div>
  );
}

export default ReimbursementResult;

