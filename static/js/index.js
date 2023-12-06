const postData = async (url, json) => {
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            // body: JSON.stringify(data)  // convert JavaScript object to JSON string
            body: json
        });
        return await response.json();
    } catch (error) {
        console.error('Error:', error);
        return await error.json();
    }
};
document.getElementById("btn-new-game").addEventListener("click", async () => {
    const url = "http://127.0.0.1:5000/game/new-game";
    const json = {"name": "amir"};
    const response = await postData(url, JSON.stringify(json));
    const gameID = response.gameID;
    console.log(`Game ID: ${gameID}`);
    window.location.href = `/game/${gameID}`;
});