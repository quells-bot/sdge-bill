import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { getBills, deleteBill } from "../api";

export default function BillsList() {
  const [bills, setBills] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchBills = async () => {
    try {
      setLoading(true);
      const data = await getBills();
      setBills(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBills();
  }, []);

  const handleDelete = async (id) => {
    if (!confirm("Are you sure you want to delete this bill?")) return;

    try {
      await deleteBill(id);
      setBills(bills.filter((bill) => bill.id !== id));
    } catch (err) {
      setError(err.message);
    }
  };

  const formatCurrency = (value) => {
    if (value === null || value === undefined) return "$0.00";
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
    }).format(value);
  };

  const formatDate = (dateStr) => {
    return new Date(dateStr + "T00:00:00").toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  const calculateTotal = (bill) => {
    return (
      (bill.gas_cost || 0) +
      (bill.electricity_delivery_cost || 0) +
      (bill.electricity_generation_cost || 0) +
      (bill.other_cost || 0)
    );
  };

  const calculateTotalKwh = (bill) => {
    return (
      (bill.electricity_on_peak_kwh || 0) +
      (bill.electricity_off_peak_kwh || 0) +
      (bill.electricity_super_off_peak_kwh || 0)
    );
  };

  if (loading) {
    return <div className="loading">Loading bills...</div>;
  }

  return (
    <div className="bills-page">
      <div className="page-header">
        <h1>Utility Bills</h1>
        <Link to="/add" className="btn-add">
          + Add Bill
        </Link>
      </div>

      {error && <div className="error-message">{error}</div>}

      {bills.length === 0 ? (
        <div className="empty-state">
          <p>No bills recorded yet.</p>
          <Link to="/add" className="btn-add">
            Add your first bill
          </Link>
        </div>
      ) : (
        <div className="bills-list">
          {bills.map((bill) => (
            <div key={bill.id} className="bill-card">
              <div className="bill-header">
                <span className="bill-date">{formatDate(bill.date)}</span>
                <span className="bill-total">{formatCurrency(calculateTotal(bill))}</span>
              </div>

              <div className="bill-details">
                <div className="detail-row">
                  <span className="detail-label">Gas:</span>
                  <span className="detail-value">
                    {formatCurrency(bill.gas_cost)} ({bill.gas_therms || 0} therms)
                  </span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">Elec. Delivery:</span>
                  <span className="detail-value">{formatCurrency(bill.electricity_delivery_cost)}</span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">Elec. Generation:</span>
                  <span className="detail-value">{formatCurrency(bill.electricity_generation_cost)}</span>
                </div>
                {bill.other_cost !== 0 && (
                  <div className="detail-row">
                    <span className="detail-label">Other:</span>
                    <span className="detail-value">{formatCurrency(bill.other_cost)}</span>
                  </div>
                )}
                <div className="detail-row">
                  <span className="detail-label">Electricity Usage:</span>
                  <span className="detail-value">{calculateTotalKwh(bill).toFixed(0)} kWh</span>
                </div>
              </div>

              <div className="bill-actions">
                <Link to={`/edit/${bill.id}`} className="btn-edit">
                  Edit
                </Link>
                <button onClick={() => handleDelete(bill.id)} className="btn-delete">
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
