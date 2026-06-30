document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("predictForm");

    if (!form) {
        return;
    }

    form.addEventListener("submit", async function (e) {
        e.preventDefault();

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

        const statusEl = document.getElementById("status");
        const predictionEl = document.getElementById("prediction");

        statusEl.textContent = "Predicting...";
        predictionEl.textContent = "—";

        try {
            const response = await fetch("http://127.0.0.1:8000/predict", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.detail || result.error || "Prediction failed");
            }

            const views = Number(result["Predicted Views"]);
            predictionEl.textContent = views.toLocaleString();

            if (views > 500000) {
                statusEl.textContent = "🔥 Viral Video Expected";
            }
            else if (views > 200000) {
                statusEl.textContent = "🚀 High Growth Expected";
            }
            else {
                statusEl.textContent = "👍 Good Performance";
            }

            loadHistory();
        }
        catch (error) {
            console.error(error);
            statusEl.textContent = "Backend connection failed";
            predictionEl.textContent = "Error";
            alert("Backend connection failed. Start the server with: python -m uvicorn backend.app:app --reload");
        }
    });

    loadHistory();
});

async function loadHistory() {
    try {
        const response = await fetch("http://127.0.0.1:8000/history");
        const data = await response.json();
        const tbody = document.querySelector("#historyTable tbody");

        if (!tbody) {
            return;
        }

        tbody.innerHTML = "";

        data.forEach(item => {
            tbody.innerHTML += `
                <tr>
                    <td>${item.subscriber_count}</td>
                    <td>${item.likes}</td>
                    <td>${item.predicted_views}</td>
                </tr>
            `;
        });
    }
    catch (error) {
        console.error(error);
    }
}