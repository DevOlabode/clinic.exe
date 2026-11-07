const planButton = document.getElementById("planButton");

planButton.addEventListener("click", (plan) => {
    fetch("/api/plan", {
        method: "POST",
        body: JSON.stringify(plan)
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
    })
    .catch(error => {
        console.error("Error:", error);
    });
});