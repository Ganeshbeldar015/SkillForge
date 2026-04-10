/**
 * api.js – Centralized API service layer
 * All backend communication goes through here.
 */

const BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

/**
 * Analyze a resume PDF for a given target role.
 *
 * @param {File}   file       - The PDF file object from the file input
 * @param {string} targetRole - The chosen role string, e.g. "AI Engineer"
 * @returns {Promise<Object>} Parsed JSON response from the backend
 */
export async function analyzeResume(file, targetRole) {
  const formData = new FormData();
  formData.append("resume", file);          // must match FastAPI param name
  formData.append("target_role", targetRole); // must match FastAPI param name

  const response = await fetch(`${BASE_URL}/analyze`, {
    method: "POST",
    body: formData,
    // Do NOT set Content-Type – browser sets it automatically with boundary
  });

  if (!response.ok) {
    // Parse backend error detail if available
    let errorMsg = `Server error: ${response.status}`;
    try {
      const errData = await response.json();
      errorMsg = errData.detail || errorMsg;
    } catch (_) {}
    throw new Error(errorMsg);
  }

  return response.json();
}

/**
 * Fetch the list of available roles from the backend.
 *
 * @returns {Promise<string[]>} Array of role name strings
 */
export async function fetchRoles() {
  const response = await fetch(`${BASE_URL}/roles`);
  if (!response.ok) throw new Error("Could not load roles from server.");
  const data = await response.json();
  return data.roles || [];
}
