document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("stock-form");
    const output = document.getElementById("output");

    form.addEventListener("submit", (e) => {
        e.preventDefault();
        const ticker = document.getElementById("ticker").value.trim();

        fetch("/api/recommendation", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ ticker }),
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.error) {
                    output.innerHTML = `<span style="color: red;">${data.error}</span>`;
                } else {
                    output.innerHTML = `
                        <strong>Ticker:</strong> ${data.Ticker}<br>
                        <strong>Accuracy:</strong> ${data.Accuracy * 100}%<br>
                        <strong>Recommendation:</strong> <span style="color: ${
                            data.Recommendation === "Buy" ? "green" : "red"
                        };">${data.Recommendation}</span>
                    `;
                }
            })
            .catch((error) => {
                output.innerHTML = `<span style="color: red;">An error occurred: ${error.message}</span>`;
            });
    });
});
