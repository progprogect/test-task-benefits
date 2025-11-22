import { useState } from 'react';
import EmployeeSelector from '../components/EmployeeSelector';
import InvoiceUpload from '../components/InvoiceUpload';
import ReimbursementResult from '../components/ReimbursementResult';
import { reimbursementAPI } from '../services/api';

function SubmitRequest() {
  const [employeeId, setEmployeeId] = useState('');
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!employeeId) {
      setError('Please select an employee');
      return;
    }

    if (!file) {
      setError('Please upload an invoice file');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await reimbursementAPI.submit(employeeId, file);
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to submit reimbursement request');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2 style={{ marginBottom: '24px' }}>Submit Reimbursement Request</h2>
      
      <div className="card">
        <form onSubmit={handleSubmit}>
          <EmployeeSelector
            value={employeeId}
            onChange={setEmployeeId}
            error={!employeeId && error ? 'Employee is required' : null}
          />

          <InvoiceUpload
            onFileSelect={setFile}
            error={!file && error ? 'Invoice file is required' : null}
          />

          {error && <div className="error">{error}</div>}

          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading || !employeeId || !file}
          >
            {loading ? 'Processing...' : 'Submit Request'}
          </button>
        </form>
      </div>

      {result && <ReimbursementResult result={result} />}
    </div>
  );
}

export default SubmitRequest;

