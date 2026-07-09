async function getMotivation() {
  const quoteBox = document.getElementById("quoteBox");
  quoteBox.innerText = "⏳ Generating...";

  try {
    const response = await fetch("http://localhost:5055/motivation");
    const data = await response.json();

    if (data.quote) {
      quoteBox.innerText = `"${data.quote}"`;
    } else {
      quoteBox.innerText = data.error || "⚠️ Could not fetch quote.";
    }
  } catch (error) {
    quoteBox.innerText = "🚫 Failed to connect to server.";
    console.error(error);
  }
}