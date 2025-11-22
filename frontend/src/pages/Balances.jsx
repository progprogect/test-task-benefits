import { useState, useEffect } from 'react';
import { employeesAPI, balancesAPI } from '../services/api';

function Balances() {
  const [employees, setEmployees] = useState([]);
  const [selectedEmployeeId, setSelectedEmployeeId] = useState('');
  const [year, setYear] = useState(new Date().getFullYear());
  const [month, setMonth] = useState(new Date().getMonth() + 1);
  const [balances, setBalances] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadEmployees();
  }, []);

  useEffect(() => {
    if (selectedEmployeeId) {
      loadBalances();
    }
  }, [selectedEmployeeId, year, month]);

  const loadEmployees = async () => {
    try {
      const response = await employeesAPI.list();
      setEmployees(response.data);
    } catch (error) {
      console.error('Failed to load employees:', error);
    }
  };

  const loadBalances = async () => {
    if (!selectedEmployeeId) return;
    
    setLoading(true);
    try {
      const response = await balancesAPI.getEmployeeBalances(selectedEmployeeId, year, month);
      setBalances(response.data);
    } catch (error) {
      console.error('Failed to load balances:', error);
      alert('Failed to load balances');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    if (amount === null || amount === undefined) return 'N/A';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  const getSelectedEmployeeName = () => {
    const employee = employees.find((e) => e.id === selectedEmployeeId);
    return employee ? `${employee.name} (${employee.employee_id})` : '';
  };

  return (
    <div>
      <h2 style={{ marginBottom: '24px' }}>Employee Balances</h2>

      <div className="card">
        <div className="form-group">
          <label htmlFor="employee-select">Select Employee</label>
          <select
            id="employee-select"
            value={selectedEmployeeId}
            onChange={(e) => setSelectedEmployeeId(e.target.value)}
            style={{ marginBottom: '16px' }}
          >
            <option value="">-- Select Employee --</option>
            {employees.map((employee) => (
              <option key={employee.id} value={employee.id}>
                {employee.name} ({employee.employee_id})
              </option>
            ))}
          </select>
        </div>

        <div style={{ display: 'flex', gap: '16px' }}>
          <div className="form-group" style={{ flex: 1 }}>
            <label htmlFor="year">Year</label>
            <input
              id="year"
              type="number"
              value={year}
              onChange={(e) => setYear(parseInt(e.target.value))}
              min="2020"
              max="2100"
            />
          </div>
          <div className="form-group" style={{ flex: 1 }}>
            <label htmlFor="month">Month</label>
            <input
              id="month"
              type="number"
              value={month}
              onChange={(e) => setMonth(parseInt(e.target.value))}
              min="1"
              max="12"
            />
          </div>
        </div>
      </div>

      {selectedEmployeeId && (
        <div className="card">
          <h3 style={{ marginBottom: '16px' }}>
            Balances for {getSelectedEmployeeName()} - {month}/{year}
          </h3>

          {loading ? (
            <div className="loading">Loading balances...</div>
          ) : balances.length > 0 ? (
            <table className="table">
              <thead>
                <tr>
                  <th>Category</th>
                  <th>Annual Limit</th>
                  <th>Annual Used</th>
                  <th>Annual Remaining</th>
                  <th>Monthly Limit</th>
                  <th>Monthly Used</th>
                  <th>Monthly Remaining</th>
                </tr>
              </thead>
              <tbody>
                {balances.map((balance) => (
                  <tr key={balance.category_id}>
                    <td>{balance.category_name}</td>
                    <td>{formatCurrency(balance.annual_limit)}</td>
                    <td>{formatCurrency(balance.annual_used)}</td>
                    <td>
                      <span
                        style={{
                          color: balance.annual_remaining >= 0 ? '#27ae60' : '#e74c3c',
                          fontWeight: 600,
                        }}
                      >
                        {formatCurrency(balance.annual_remaining)}
                      </span>
                    </td>
                    <td>{formatCurrency(balance.monthly_limit)}</td>
                    <td>{formatCurrency(balance.monthly_used)}</td>
                    <td>
                      <span
                        style={{
                          color: balance.monthly_remaining >= 0 ? '#27ae60' : '#e74c3c',
                          fontWeight: 600,
                        }}
                      >
                        {formatCurrency(balance.monthly_remaining)}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="loading">No balance data available</div>
          )}
        </div>
      )}
    </div>
  );
}

export default Balances;

