import { useState, useEffect } from 'react';
import { employeesAPI } from '../services/api';

function EmployeeSelector({ value, onChange, error }) {
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadEmployees();
  }, []);

  const loadEmployees = async () => {
    try {
      const response = await employeesAPI.list();
      setEmployees(response.data);
    } catch (error) {
      console.error('Failed to load employees:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading employees...</div>;
  }

  return (
    <div className="form-group">
      <label htmlFor="employee">Select Employee *</label>
      <select
        id="employee"
        value={value || ''}
        onChange={(e) => onChange(e.target.value)}
        required
      >
        <option value="">-- Select Employee --</option>
        {employees.map((employee) => (
          <option key={employee.id} value={employee.id}>
            {employee.name} ({employee.employee_id})
          </option>
        ))}
      </select>
      {error && <div className="error">{error}</div>}
    </div>
  );
}

export default EmployeeSelector;

