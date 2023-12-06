const postData = async (url, data) => {
    try {
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(data), // convert JavaScript object to JSON string
        });
        return await response.json();
    } catch (error) {
        console.error("Error:", error);
        return await error.json();
    }
};
document.getElementById("btn-new-game").addEventListener("click", async () => {
    const url = "/game/new-game";
    const name = document.getElementById("input-player-name").value;
    const data = { name: name };
    const response = await postData(url, data);
    const gameID = response.gameID;
    console.log(`Game ID: ${gameID}`);
    window.location.href = `/game/${gameID}`;
});
