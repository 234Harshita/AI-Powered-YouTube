document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("predict-form");
    const result = document.getElementById("result");

    if (form) {
        form.addEventListener("submit", async (e) => {
            e.preventDefault();
            const url = document.getElementById("video-url")?.value || "";
            result.textContent = `Prediction request for: ${url}`;
        });
    }
});
