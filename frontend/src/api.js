const API_BASE = "/api";

export async function getBills() {
  const response = await fetch(`${API_BASE}/bills`);
  if (!response.ok) throw new Error("Failed to fetch bills");
  return response.json();
}

export async function getBill(id) {
  const response = await fetch(`${API_BASE}/bills/${id}`);
  if (!response.ok) throw new Error("Failed to fetch bill");
  return response.json();
}

export async function createBill(bill) {
  const response = await fetch(`${API_BASE}/bills`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(bill),
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || "Failed to create bill");
  }
  return response.json();
}

export async function updateBill(id, bill) {
  const response = await fetch(`${API_BASE}/bills/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(bill),
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || "Failed to update bill");
  }
  return response.json();
}

export async function deleteBill(id) {
  const response = await fetch(`${API_BASE}/bills/${id}`, {
    method: "DELETE",
  });
  if (!response.ok) throw new Error("Failed to delete bill");
  return response.json();
}
