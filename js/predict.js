/**
 * Prediction page API utilities
 */

const STORAGE_KEY = "preferred-backend-url";
const API_BASES = [
    window.__API_BASE__,
    `http://${window.location.hostname}:8000`,
    "http://localhost:8000",
    "http://127.0.0.1:8000"
].filter(Boolean);

let backendAvailable = false;
let currentBackendUrl = null;
let hasConnectedBefore = false;
let lastSuccessfulProbe = 0;

function persistBackendUrl(base) {
    if (!base) return;
    try {
        window.localStorage.setItem(STORAGE_KEY, base);
    } catch (error) {
        console.debug("Could not persist backend URL:", error);
    }
}

function getStoredBackendUrl() {
    try {
        return window.localStorage.getItem(STORAGE_KEY) || null;
    } catch (error) {
        return null;
    }
}

function updateConnectionStatus(isConnected) {
    const statusIndicator = document.getElementById("backend-status");
    if (!statusIndicator) return;

    statusIndicator.textContent = isConnected ? "🟢 Backend Connected" : "🔴 Backend Disconnected";
    statusIndicator.style.color = isConnected ? "#4CAF50" : "#f44336";
}

async function findWorkingBackend(force = false) {
    const storedBackendUrl = getStoredBackendUrl();
    const candidateBases = storedBackendUrl ? [storedBackendUrl, ...API_BASES.filter(base => base !== storedBackendUrl)] : API_BASES;

    if (!force && currentBackendUrl && backendAvailable && Date.now() - lastSuccessfulProbe < 60000) {
        updateConnectionStatus(true);
        return currentBackendUrl;
    }

    for (const base of candidateBases) {
        try {
            const response = await fetch(`${base}/health`, {
                method: "GET",
                headers: { "Content-Type": "application/json" }
            });

            if (response.ok) {
                currentBackendUrl = base;
                backendAvailable = true;
                hasConnectedBefore = true;
                lastSuccessfulProbe = Date.now();
                persistBackendUrl(base);
                updateConnectionStatus(true);
                console.log(`✅ Backend found at: ${base}`);
                return base;
            }
        } catch (error) {
            console.debug(`Cannot reach backend at ${base}:`, error.message);
        }
    }

    if (currentBackendUrl && hasConnectedBefore) {
        backendAvailable = true;
        updateConnectionStatus(true);
        return currentBackendUrl;
    }

    currentBackendUrl = null;
    backendAvailable = false;
    updateConnectionStatus(false);
    console.warn("❌ No working backend found");
    return null;
}

async function requestJson(path, options = {}, maxRetries = 3) {
    let lastError = null;

    if (!currentBackendUrl || !backendAvailable || Date.now() - lastSuccessfulProbe > 60000) {
        const workingBackend = await findWorkingBackend();
        if (!workingBackend) {
            throw new Error("Backend connection failed. Start the backend with: python -m uvicorn backend.app:app --reload");
        }
    }

    for (let attempt = 1; attempt <= maxRetries; attempt += 1) {
        try {
            const response = await fetch(`${currentBackendUrl}${path}`, {
                ...options,
                headers: {
                    "Content-Type": "application/json",
                    ...(options.headers || {})
                }
            });

            const data = await response.json().catch(() => ({}));

            if (!response.ok) {
                throw new Error(data.detail || data.error || `HTTP ${response.status}`);
            }

            backendAvailable = true;
            hasConnectedBefore = true;
            lastSuccessfulProbe = Date.now();
            updateConnectionStatus(true);
            return data;
        } catch (error) {
            lastError = error;
            console.error(`❌ Attempt ${attempt} failed:`, error.message);

            if (attempt < maxRetries) {
                const delayMs = Math.pow(2, attempt - 1) * 500;
                await new Promise(resolve => setTimeout(resolve, delayMs));
            }
        }
    }

    if (currentBackendUrl && hasConnectedBefore) {
        updateConnectionStatus(true);
        return null;
    }

    updateConnectionStatus(false);
    throw lastError || new Error("Backend connection failed");
}

async function loadHistory() {
    try {
        const data = await requestJson("/history", {}, 2);
        const tbody = document.querySelector("#history-table tbody");
        if (!tbody) return;

        tbody.innerHTML = "";

        if (!Array.isArray(data) || data.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="3" style="text-align: center; color: #999;">No predictions yet</td>
                </tr>
            `;
            return;
        }

        data.forEach(item => {
            tbody.innerHTML += `
                <tr>
                    <td>${Number(item.subscriber_count || 0).toLocaleString()}</td>
                    <td>${Number(item.likes || 0).toLocaleString()}</td>
                    <td>${Number(item.predicted_views || 0).toLocaleString()}</td>
                </tr>
            `;
        });
    } catch (error) {
        console.error("Failed to load history:", error);
    }
}

document.addEventListener("DOMContentLoaded", async () => {
    const form = document.getElementById("predict-form");
    const statusEl = document.getElementById("status");
    const predictionEl = document.getElementById("prediction");
    const submitButton = form?.querySelector("button[type='submit']") || null;

    if (!document.getElementById("backend-status")) {
        const header = document.querySelector("h1");
        if (header) {
            const statusDiv = document.createElement("div");
            statusDiv.id = "backend-status";
            statusDiv.style.cssText = "display:inline-block;margin-left:12px;font-size:14px;font-weight:600;padding:6px 10px;border-radius:999px;background:rgba(255,255,255,0.12);";
            header.appendChild(statusDiv);
        }
    }

    await findWorkingBackend();

    setInterval(async () => {
        if (!backendAvailable || !currentBackendUrl) {
            await findWorkingBackend();
        }
    }, 10000);

    if (!form || !statusEl || !predictionEl) {
        console.warn("Prediction page elements not found");
        return;
    }

    const setBusy = (isBusy) => {
        if (submitButton) {
            submitButton.disabled = isBusy;
            submitButton.textContent = isBusy ? "⏳ Predicting..." : "🚀 Predict Views";
        }
    };

    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        const data = {
            title_length: Number(document.getElementById("title_length").value),
            upload_hour: Number(document.getElementById("upload_hour").value),
            category: document.getElementById("category").value,
            tags_count: Number(document.getElementById("tags_count").value),
            duration_min: Number(document.getElementById("duration_min").value),
            thumbnail_score: Number(document.getElementById("thumbnail_score").value),
            seo_score: Number(document.getElementById("seo_score").value),
            ctr_percent: Number(document.getElementById("ctr_percent").value),
            likes: Number(document.getElementById("likes").value),
            comments: Number(document.getElementById("comments").value),
            subscriber_count: Number(document.getElementById("subscriber_count").value),
            viral_score: Number(document.getElementById("viral_score").value)
        };

        statusEl.textContent = "⏳ Predicting...";
        predictionEl.textContent = "—";
        setBusy(true);

        try {
            const result = await requestJson("/predict", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data)
            }, 3);

            const views = Number(result["Predicted Views"]);
            predictionEl.textContent = views.toLocaleString();

            if (views > 500000) {
                statusEl.textContent = "🔥 Viral Video Expected";
            } else if (views > 200000) {
                statusEl.textContent = "🚀 High Growth Expected";
            } else {
                statusEl.textContent = "👍 Good Performance";
            }

            await loadHistory();
        } catch (error) {
            console.error("Prediction failed:", error);
            statusEl.textContent = "❌ Backend connection failed";
            predictionEl.textContent = "Error";
            alert("Backend is not reachable. Start it with: python -m uvicorn backend.app:app --reload");
        } finally {
            setBusy(false);
        }
    });

    await loadHistory();
});