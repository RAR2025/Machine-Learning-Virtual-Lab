const API_BASE_URL = "";

async function handle(response) {
  if (!response.ok) {
    let detail = `Request failed with status ${response.status}`;
    try {
      const body = await response.json();
      if (body && body.detail) {
        detail = Array.isArray(body.detail) ? body.detail.map((d) => d.msg || JSON.stringify(d)).join("; ") : body.detail;
      }
    } catch {
      // ignore JSON parse errors
    }
    throw new Error(detail);
  }
  return response.json();
}

function unwrapTrain(payload) {
  // New backend returns {results, comparison, meta}; legacy returned object/array.
  if (payload && typeof payload === "object" && "results" in payload) return payload;
  return { results: payload, comparison: null, meta: null };
}

export async function analyzeCode(code, experimentId) {
  const response = await fetch(`${API_BASE_URL}/api/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ code, experiment_id: experimentId || null }),
  });
  return handle(response);
}

export async function cleanData(experimentId) {
  const response = await fetch(`${API_BASE_URL}/api/clean`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ experiment_id: experimentId || null, code: "" }),
  });
  return handle(response);
}

export async function trainModel(encoding, opts = {}) {
  const response = await fetch(`${API_BASE_URL}/api/train`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      encoding,
      experiment_id: opts.experimentId || null,
      model: opts.model || null,
      test_size: opts.testSize ?? null,
      random_state: opts.randomState ?? null,
    }),
  });
  const payload = await handle(response);
  return unwrapTrain(payload);
}

export async function listModels(experimentId, problemType) {
  const q = new URLSearchParams();
  if (experimentId) q.set("experiment_id", experimentId);
  if (problemType) q.set("problem_type", problemType);
  const response = await fetch(`${API_BASE_URL}/api/models?${q.toString()}`);
  return handle(response);
}

export async function selectModel(model, experimentId) {
  const response = await fetch(`${API_BASE_URL}/api/models/select`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ model, experiment_id: experimentId || null }),
  });
  return handle(response);
}

export async function configureSplit(experimentId, testSize, randomState) {
  const response = await fetch(`${API_BASE_URL}/api/split`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ experiment_id: experimentId || null, test_size: testSize, random_state: randomState }),
  });
  return handle(response);
}
