const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

export function getApiBaseUrl() {
  return API_BASE_URL;
}

export function getVerificationReportUrl(requestId) {
  return `${API_BASE_URL}/deletion-requests/${encodeURIComponent(requestId)}/report`;
}

async function request(path, options = {}) {
  const headers = { ...options.headers };
  if (options.body && !headers["Content-Type"]) {
    headers["Content-Type"] = "application/json";
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    const detail = data.detail;
    const message = Array.isArray(detail)
      ? detail.map((item) => item.msg || JSON.stringify(item)).join('; ')
      : typeof detail === 'string'
        ? detail
        : detail
          ? JSON.stringify(detail)
          : `Request failed: ${response.status}`;
    throw new Error(message);
  }

  return data;
}

export function getHealthCheck() {
  return request("/health").catch(() => request("/"));
}

export function getResources() {
  return request("/resources");
}

export function getDependencies(resourceId) {
  return request(
    `/resources/${encodeURIComponent(resourceId)}/dependencies`
  );
}

export function getDeletionRequests() {
  return request("/deletion-requests");
}

export function getDeletionRequest(requestId) {
  return request(`/deletion-requests/${encodeURIComponent(requestId)}`);
}

export function getVerificationReport(requestId) {
  return request(`/deletion-requests/${encodeURIComponent(requestId)}/report`);
}

export function createDeletionRequest(resourceId, simulateFailure = false) {
  const id = typeof resourceId === 'string' ? resourceId : resourceId?.id;
  if (!id) throw new Error('A registered resource ID is required.');
  return request("/deletion-requests", {
    method: "POST",
    body: JSON.stringify({
      resource_id: id,
      simulate_failure: simulateFailure,
    }),
  });
}

export function getExperimentComparison() {
  return request("/experiments/compare");
}

export function runExperiment(configuration) {
  return request('/experiments/run', {
    method: 'POST',
    body: JSON.stringify(configuration),
  });
}

export function experimentExportUrl(experimentId, kind) {
  const allowed = new Set(['trials.csv', 'aggregates.csv', 'report.md']);
  if (!allowed.has(kind)) throw new Error('Unsupported experiment export.');
  return `${API_BASE_URL}/experiments/${encodeURIComponent(experimentId)}/${kind}`;
}
