async function loadDashboard() {
    try {
        const statsResponse = await fetch("http://127.0.0.1:8000/stats");
        const stats = await statsResponse.json();

        document.getElementById("totalPredictions").textContent = stats.total_predictions;
        document.getElementById("averageViews").textContent = Number(stats.average_views).toLocaleString();

        const historyResponse = await fetch("http://127.0.0.1:8000/history");
        const history = await historyResponse.json();

        const labels = [];
        const values = [];

        history.slice().reverse().forEach(item => {
            labels.push("Prediction " + item.id);
            values.push(item.predicted_views);
        });

        const ctx = document.getElementById("myChart");

        if (ctx) {
            new Chart(ctx, {
                type: "line",
                data: {
                    labels: labels,
                    datasets: [{
                        label: "Predicted Views",
                        data: values,
                        borderWidth: 3,
                        fill: false,
                        borderColor: "#38bdf8"
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false
                }
            });
        }
    }
    catch (error) {
        console.error("Dashboard Error:", error);
    }
}

document.addEventListener("DOMContentLoaded", loadDashboard);