import { reactive } from "vue";

export const session = reactive({
  user: null,
  csrfToken: "",
  checked: false,
});

export async function apiRequest(path, options = {}) {
  const method = String(options.method || "GET").toUpperCase();
  const hasBody = options.body !== undefined && options.body !== null;
  const headers = {
    "X-Requested-With": "DentalSystem",
    ...(hasBody ? { "Content-Type": "application/json" } : {}),
    ...(session.csrfToken && method !== "GET" ? { "X-CSRF-Token": session.csrfToken } : {}),
    ...(options.headers || {}),
  };

  let response;
  try {
    response = await fetch(path, {
      method,
      credentials: "same-origin",
      headers,
      body: hasBody
        ? typeof options.body === "string"
          ? options.body
          : JSON.stringify(options.body)
        : undefined,
    });
  } catch {
    throw new Error(
      "Cannot reach the server. Start the Python backend and open the local server URL.",
    );
  }

  const data = await response.json().catch(() => ({}));
  if (data.csrf_token) session.csrfToken = data.csrf_token;
  if (!response.ok) {
    throw new Error(data.error || "Something went wrong.");
  }
  return data;
}

export async function refreshSession() {
  const data = await apiRequest("/api/session");
  session.user = data.user || null;
  session.csrfToken = data.csrf_token || "";
  session.checked = true;
  return session.user;
}

export async function signOut() {
  await apiRequest("/api/logout", { method: "POST", body: {} });
  session.user = null;
  session.csrfToken = "";
}
