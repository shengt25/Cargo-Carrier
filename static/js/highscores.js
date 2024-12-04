// function to fetch data from API
const getData = async (url) => {
    const response = await fetch(url);
    if (!response.ok) throw new Error("Invalid server input");
    const data = await response.json();
    // console.log(data)
    return data;
};

const renderHighScore = async () => {
    const tableBody = document.querySelector("#table-body");
    // console.log(tableBody)
    // const tr = document.createElement('tr')
    // tableBody.appendChild(tr)
    const highScores = await getData("get-highscore");
    console.log(highScores);

    htmls = highScores
        .map((player) => {
            return `
            <tr>
                <th scope="row">${player.rank}</th>
                <td>${player.screen_name}</td>
                <td>${player.score}</td>
                <td>${player.money}</td>
                <td>${player.fuel}</td>
                <td>${player.time}</td>
                <td>${player.emission}</td>
            </tr>
        `;
        })
        .join("");
    tableBody.innerHTML = htmls;
};

renderHighScore();
