// =============================
// 🌙 DARK MODE TOGGLE
// =============================
function toggleDark() {
    document.body.classList.toggle("bg-dark");
    document.body.classList.toggle("text-white");
}

// =============================
// 📊 CHART.JS GRAPH FUNCTION
// =============================
function loadChart(labels, data) {

    const ctx = document.getElementById("chart");

    if (!ctx) return;

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Progress %',
                data: data,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            }
        }
    });
}

// =============================
// 🔥 SIMPLE ANIMATION EFFECT
// =============================
function animateCards() {
    const cards = document.querySelectorAll(".card");

    cards.forEach((card, index) => {
        card.style.opacity = 0;
        card.style.transform = "translateY(20px)";

        setTimeout(() => {
            card.style.transition = "0.5s";
            card.style.opacity = 1;
            card.style.transform = "translateY(0)";
        }, index * 100);
    });
}

// =============================
// 🚀 PAGE LOAD EVENTS
// =============================
document.addEventListener("DOMContentLoaded", function () {

    // Run animation
    animateCards();

    // Load chart if data exists
    if (typeof skillLabels !== "undefined" && typeof skillData !== "undefined") {
        loadChart(skillLabels, skillData);
    }

});