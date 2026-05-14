document.getElementById("booking-form").addEventListener("submit", function(event) {
    event.preventDefault();

    let from = document.getElementById("from").value;
    let to = document.getElementById("to").value;
    let date = document.getElementById("date").value;
    let seats = document.getElementById("seats").value;

    let resultsDiv = document.getElementById("results");
    resultsDiv.innerHTML = `<p>Searching buses from <strong>${from}</strong> to <strong>${to}</strong> on <strong>${date}</strong> for <strong>${seats}</strong> seat(s)...</p>`;

    // Simulating a server response
    setTimeout(() => {
        resultsDiv.innerHTML += `<p>Available buses found! Proceed to booking.</p>`;
    }, 2000);
});
