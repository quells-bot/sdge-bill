import { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { getBill, createBill, updateBill } from "../api";

const initialFormState = {
  date: new Date().toISOString().split("T")[0],
  gas_cost: "",
  electricity_delivery_cost: "",
  electricity_generation_cost: "",
  other_cost: "",
  gas_therms: "",
  electricity_on_peak_kwh: "",
  electricity_off_peak_kwh: "",
  electricity_super_off_peak_kwh: "",
};

export default function BillForm() {
  const navigate = useNavigate();
  const { id } = useParams();
  const isEditing = Boolean(id);

  const [form, setForm] = useState(initialFormState);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (isEditing) {
      setLoading(true);
      getBill(id)
        .then((bill) => {
          setForm({
            date: bill.date,
            gas_cost: bill.gas_cost ?? "",
            electricity_delivery_cost: bill.electricity_delivery_cost ?? "",
            electricity_generation_cost: bill.electricity_generation_cost ?? "",
            other_cost: bill.other_cost ?? "",
            gas_therms: bill.gas_therms ?? "",
            electricity_on_peak_kwh: bill.electricity_on_peak_kwh ?? "",
            electricity_off_peak_kwh: bill.electricity_off_peak_kwh ?? "",
            electricity_super_off_peak_kwh: bill.electricity_super_off_peak_kwh ?? "",
          });
        })
        .catch((err) => setError(err.message))
        .finally(() => setLoading(false));
    }
  }, [id, isEditing]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    const billData = {
      date: form.date,
      gas_cost: parseFloat(form.gas_cost) || 0,
      electricity_delivery_cost: parseFloat(form.electricity_delivery_cost) || 0,
      electricity_generation_cost: parseFloat(form.electricity_generation_cost) || 0,
      other_cost: parseFloat(form.other_cost) || 0,
      gas_therms: parseFloat(form.gas_therms) || 0,
      electricity_on_peak_kwh: parseFloat(form.electricity_on_peak_kwh) || 0,
      electricity_off_peak_kwh: parseFloat(form.electricity_off_peak_kwh) || 0,
      electricity_super_off_peak_kwh: parseFloat(form.electricity_super_off_peak_kwh) || 0,
    };

    try {
      if (isEditing) {
        await updateBill(id, billData);
      } else {
        await createBill(billData);
      }
      navigate("/");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading && isEditing) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <div className="form-page">
      <h1>{isEditing ? "Edit Bill" : "Add Bill"}</h1>

      <form onSubmit={handleSubmit} className="bill-form">
        {error && <div className="error-message">{error}</div>}

        <div className="form-group">
          <label htmlFor="gas_cost">Gas ($)</label>
          <input
            type="number"
            id="gas_cost"
            name="gas_cost"
            value={form.gas_cost}
            onChange={handleChange}
            step="0.01"
            placeholder="0.00"
          />
        </div>

        <div className="form-group">
          <label htmlFor="electricity_delivery_cost">Electricity Delivery ($)</label>
          <input
            type="number"
            id="electricity_delivery_cost"
            name="electricity_delivery_cost"
            value={form.electricity_delivery_cost}
            onChange={handleChange}
            step="0.01"
            placeholder="0.00"
          />
        </div>

        <div className="form-group">
          <label htmlFor="electricity_generation_cost">Electricity Generation ($)</label>
          <input
            type="number"
            id="electricity_generation_cost"
            name="electricity_generation_cost"
            value={form.electricity_generation_cost}
            onChange={handleChange}
            step="0.01"
            placeholder="0.00"
          />
        </div>

        <div className="form-group">
          <label htmlFor="other_cost">Other ($)</label>
          <input
            type="number"
            id="other_cost"
            name="other_cost"
            value={form.other_cost}
            onChange={handleChange}
            step="0.01"
            placeholder="0.00"
          />
        </div>

        <div className="form-group">
          <label htmlFor="gas_therms">Gas (therms)</label>
          <input
            type="number"
            id="gas_therms"
            name="gas_therms"
            value={form.gas_therms}
            onChange={handleChange}
            step="0.01"
            placeholder="0"
          />
        </div>

        <div className="form-group">
          <label htmlFor="electricity_on_peak_kwh">Electricity On-Peak (kWh)</label>
          <input
            type="number"
            id="electricity_on_peak_kwh"
            name="electricity_on_peak_kwh"
            value={form.electricity_on_peak_kwh}
            onChange={handleChange}
            step="0.01"
            placeholder="0"
          />
        </div>

        <div className="form-group">
          <label htmlFor="electricity_off_peak_kwh">Electricity Off-Peak (kWh)</label>
          <input
            type="number"
            id="electricity_off_peak_kwh"
            name="electricity_off_peak_kwh"
            value={form.electricity_off_peak_kwh}
            onChange={handleChange}
            step="0.01"
            placeholder="0"
          />
        </div>

        <div className="form-group">
          <label htmlFor="electricity_super_off_peak_kwh">Electricity Super Off-Peak (kWh)</label>
          <input
            type="number"
            id="electricity_super_off_peak_kwh"
            name="electricity_super_off_peak_kwh"
            value={form.electricity_super_off_peak_kwh}
            onChange={handleChange}
            step="0.01"
            placeholder="0"
          />
        </div>

        <div className="form-actions">
          <input
            type="date"
            id="date"
            name="date"
            value={form.date}
            onChange={handleChange}
            required
          />
          <button type="submit" className="btn-save" disabled={loading}>
            {loading ? "Saving..." : "Save"}
          </button>
        </div>
      </form>
    </div>
  );
}
