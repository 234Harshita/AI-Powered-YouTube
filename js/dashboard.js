async function fetchDashboardJson(path) {
    const storedBackendUrl = (() => {
        try {
            return window.localStorage.getItem("preferred-backend-url") || null;
        } catch (error) {
            return null;
        }
    })();

    const candidateBases = storedBackendUrl ? [storedBackendUrl, "http://127.0.0.1:8000", "http://localhost:8000"] : ["http://127.0.0.1:8000", "http://localhost:8000"];

    for (const base of candidateBases) {
        try {
            const response = await fetch(`${base}${path}`);
            if (!response.ok) continue;
            const data = await response.json();
            if (base && base !== storedBackendUrl) {
                try {
                    window.localStorage.setItem("preferred-backend-url", base);
                } catch (error) {
                    console.debug("Could not persist backend URL:", error);
                }
            }
            return data;
        } catch (error) {
            console.debug(`Dashboard probe failed for ${base}:`, error);
        }
    }

    throw new Error("Dashboard backend unavailable");
}

async function loadDashboard() {
    const totalEl = document.getElementById("totalPredictions");
    const averageEl = document.getElementById("averageViews");
    const chartEl = document.getElementById("myChart");

    try {
        const stats = await fetchDashboardJson("/stats");

        if (totalEl) totalEl.textContent = Number(stats.total_predictions || 0).toLocaleString();
        if (averageEl) averageEl.textContent = Number(stats.average_views || 0).toLocaleString();

        const history = await fetchDashboardJson("/history");
        const labels = [];
        const values = [];

        history.slice().reverse().forEach(item => {
            labels.push("P" + item.id);
            values.push(Number(item.predicted_views || 0));
        });

        if (chartEl) {
            if (window.dashboardChart) {
                window.dashboardChart.destroy();
            }

            window.dashboardChart = new Chart(chartEl, {
                type: "line",
                data: {
                    labels: labels.length ? labels : ["No data"],
                    datasets: [{
                        label: "Predicted Views",
                        data: values.length ? values : [0],
                        borderWidth: 3,
                        tension: 0.35,
                        fill: false,
                        borderColor: "#ff8a3d",
                        backgroundColor: "rgba(255,138,61,0.2)",
                        pointBackgroundColor: "#fff"
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { labels: { color: "#f8fafc" } }
                    },
                    scales: {
                        x: { ticks: { color: "#cbd5e1" }, grid: { color: "rgba(255,255,255,0.08)" } },
                        y: { ticks: { color: "#cbd5e1" }, grid: { color: "rgba(255,255,255,0.08)" } }
                    }
                }
            });
        }
    } catch (error) {
        console.error("Dashboard Error:", error);
        if (totalEl) totalEl.textContent = "—";
        if (averageEl) averageEl.textContent = "—";
        if (chartEl && !chartEl.dataset.fallback) {
            chartEl.innerHTML = '<div class="empty-state">Backend is currently unavailable.</div>';
            chartEl.dataset.fallback = "1";
        }
    }
}

document.addEventListener("DOMContentLoaded", loadDashboard);