const API = (localStorage.getItem("apiBase") || "http://127.0.0.1:8000").replace(/\/+$/, "");

function token() {
  return localStorage.getItem("token");
}

async function api(path, options = {}) {
  const headers = { ...(options.headers || {}) };
  if (options.body !== undefined && !headers["Content-Type"]) {
    headers["Content-Type"] = "application/json";
  }
  if (token()) headers.Authorization = "Bearer " + token();

  let response;
  try {
    response = await fetch(API + path, { ...options, headers });
  } catch (error) {
    if (error instanceof TypeError) {
      throw new Error(`Cannot reach the API at ${API}. Check that the backend is running and CORS allows this frontend origin.`);
    }
    throw error;
  }

  let data;
  try {
    data = await response.json();
  } catch {
    if (response.ok) throw new Error("The API returned an invalid response.");
    data = {};
  }
  if (!response.ok) {
    const requestError = new Error(data.detail || `Request failed (${response.status})`);
    requestError.status = response.status;
    throw requestError;
  }
  return data;
}

function logout() {
  localStorage.removeItem("token");
  localStorage.removeItem("user");
  location.href = "index.html";
}
