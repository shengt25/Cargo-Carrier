var selectedAirport;

async function getData(url) {
    const response = await fetch(url);
    if (!response.ok) throw new Error("Invalid server input");
    return await response.json();
}

async function postData(url, data) {
    try {
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(data), // convert JavaScript object to JSON string
        });
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error("Error:", error);
        return await error.json();
    }
}

function getGameIDFromUrl() {
    const pathParts = window.location.pathname.split("/");
    return pathParts[pathParts.length - 1];
}

const updatePlayerStatus = async (gameID) => {
    const playerResponse = await getData(`/game/${gameID}/get-player-data`);
    const playerData = playerResponse.player;
    const name = document.getElementById("player-name");
    const time = document.getElementById("time-left");
    const money = document.getElementById("money");
    const fuel = document.getElementById("fuel");
    const emission = document.getElementById("co2-emission");
    const location = document.getElementById("location");

    name.innerText = `${playerData.name}`;
    time.innerText = `${playerData.time}`;
    money.innerText = `${playerData.money}`;
    fuel.innerText = `${playerData.fuel}`;
    emission.innerText = `${playerData.emission}`;
    location.innerText = `${playerData.location}`;
};

function updateFlyProtocol(airportData) {
    const flyProtocol = document.getElementById("flight-protocol");
    flyProtocol.innerHTML = `
        <h2>Fly Protocol</h2>
        <p>ICAO code: ${airportData.ident}</p>
        <p>Airport Name: ${airportData.name}</p>
        <p>Country: ${airportData.country_name}</p>
        <p>Fuel: ${airportData.fuel ? airportData.fuel : 0}</p>
        <p>Money: ${airportData.reward ? airportData.reward : 0}</p>
        <p>CO2: ${airportData.emission ? airportData.emission : 0}</p>
    `;
}

function showOptionsModal() {
    const modal = document.getElementById("options-modal");
    modal.showModal();
}

function hideOptionsModal() {
    const modal = document.getElementById("options-modal");
    modal.close();
}

function isGameFinish(playerData) {
    return playerData.finish === 1;
}

function initMap() {
    const map = L.map("map", { tap: false });
    const airportMarkerGroup = L.featureGroup().addTo(map);
    L.tileLayer("https://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}", {
        maxZoom: 20,
        subdomains: ["mt0", "mt1", "mt2", "mt3"],
    }).addTo(map);
    map.setView([60, 24], 3);
    return [map, airportMarkerGroup];
}

async function updateMap(gameID, map, airportMarkerGroup) {
    console.log("updating map");

    const airportsResponse = await getData(`/game/${gameID}/get-airports-data`);
    const airportsData = airportsResponse.airports;

    const greenIcon = L.icon({
        iconUrl:
            "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png",
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
    });
    // out range airports
    const redIcon = L.icon({
        iconUrl:
            "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png",
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
    });

    airportMarkerGroup.clearLayers();
    Object.keys(airportsData).forEach((ident) => {
        const airportData = airportsData[ident];
        const reachFuel = airportData.reach_fuel;
        const reachTime = airportData.reach_time;

        if (airportData.current === true) {
            const airportMarker = L.marker(
                [airportData.latitude_deg, airportData.longitude_deg],
                { icon: redIcon },
            ).addTo(airportMarkerGroup);
            airportMarker.bindPopup(
                `<h2>${airportData.country_name}</h2><p>${airportData.name} <b>(${airportData.ident})</b></p>`,
            );
            airportMarker.on("click", () => {
                console.log(airportData);
                document.getElementById("btn-fly").disabled = true;
                updateFlyProtocol(airportData);
                selectedAirport = airportData;
            });
        } else if (reachFuel === false || reachTime === false) {
            const airportMarker = L.marker(
                [airportData.latitude_deg, airportData.longitude_deg],
                { icon: redIcon },
            ).addTo(airportMarkerGroup);
            airportMarker.bindPopup(
                `<h2>${airportData.country_name}</h2><p>${airportData.name} <b>(${airportData.ident})</b></p>`,
            );
            airportMarker.on("click", () => {
                console.log(airportData);
                document.getElementById("btn-fly").disabled = true;
                updateFlyProtocol(airportData);
                selectedAirport = airportData;
            });
        } else {
            const airportMarker = L.marker(
                [airportData.latitude_deg, airportData.longitude_deg],
                { icon: greenIcon },
            ).addTo(airportMarkerGroup);
            airportMarker.bindPopup(
                `<h2>${airportData.country_name}</h2><p>${airportData.name} <b>(${airportData.ident})</b></p>`,
            );
            airportMarker.on("click", () => {
                console.log(airportData);
                document.getElementById("btn-fly").disabled = false;
                updateFlyProtocol(airportData);
                selectedAirport = airportData;
            });
        }
    });
    map.fitBounds(airportMarkerGroup.getBounds());
}

(() => {
    const gameID = getGameIDFromUrl();
    const [map, airportMarkerGroup] = initMap();
    updateMap(gameID, map, airportMarkerGroup);
    updatePlayerStatus(gameID);

    const btnHire = document.getElementById("dice-option");
    const btnMyself = document.getElementById("unload-option");
    const btnFly = document.getElementById("btn-fly");
    btnMyself.addEventListener("click", async () => {
        try {
            const jsonData = { option: 1 };
            await postData(`/game/${gameID}/unload`, jsonData);
            updateMap(gameID, map, airportMarkerGroup);
            updatePlayerStatus(gameID);
            hideOptionsModal();
        } catch (error) {
            console.error(error);
        }
    });
    btnHire.addEventListener("click", async () => {
        try {
            const jsonData = { option: 0 };
            await postData(`/game/${gameID}/unload`, jsonData);
            updateMap(gameID, map, airportMarkerGroup);
            updatePlayerStatus(gameID);
            hideOptionsModal();
        } catch (error) {
            console.error(error);
        }
    });
    btnFly.addEventListener("click", async () => {
        try {
            const jsonData = { ident: selectedAirport.ident };
            await postData(`/game/${gameID}/fly`, jsonData);
            console.log("try to update map");

            updateMap(gameID, map, airportMarkerGroup);
            updatePlayerStatus(gameID);
            showOptionsModal();
        } catch (error) {
            console.error(error);
        }
    });
})();
