// global variables
// const gameId = 'c6c77c1f22e43915d624e7d5c50001df4ea065bb'
// current airport
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

// initialize the map
const map = L.map("map", { tap: false });

const airportMarkers = L.featureGroup().addTo(map);
// add map
L.tileLayer("https://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}", {
    maxZoom: 20,
    subdomains: ["mt0", "mt1", "mt2", "mt3"],
}).addTo(map);
map.setView([60, 24], 3);

// function to fetch data from API
const getData = async (url) => {
    const response = await fetch(url);
    if (!response.ok) throw new Error("Invalid server input");
    const data = await response.json();
    return data;
};

// function to post data to API
const postData = async (url, json) => {
    try {
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            // body: JSON.stringify(data)  // convert JavaScript object to JSON string
            body: json,
        });
        return await response.json();
    } catch (error) {
        console.error("Error:", error);
        return await error.json();
    }
};

const getGameIdFromUrl = () => {
    const pathParts = window.location.pathname.split("/");
    return pathParts[pathParts.length - 1];
};

// main function to set up the game
const gameSetup = async (gameId) => {
    try {
        airportMarkers.clearLayers();
        const status = await getData(`/game/${gameId}/get-player-data`);

        const name = document.getElementById("player-name");
        const time = document.getElementById("time-left");
        const money = document.getElementById("money");
        const fuel = document.getElementById("fuel");
        const emission = document.getElementById("co2-emission");
        const location = document.getElementById("location");

        console.log(status); // Check the structure of the returned data

        // Update your HTML elements with the retrieved data
        name.innerText = `${status.player.name}`;
        time.innerText = `${status.player.time}`;
        money.innerText = `${status.player.money}`;
        fuel.innerText = `${status.player.fuel}`;
        emission.innerText = `${status.player.emission}`;
        location.innerText = `${status.player.location}`;

        const airportsData = await getData(`/game/${gameId}/get-airports-data`);
        const airports = airportsData.airports;

        for (const airportCode in airports) {
            if (airports.hasOwnProperty(airportCode)) {
                const airport = airports[airportCode];
                const name = airport.name;
                const latitude = airport.latitude_deg;
                const longitude = airport.longitude_deg;

                let marker;

                if (airportCode === status.player.location) {
                    marker = L.marker([latitude, longitude], {
                        icon: greenIcon,
                    }).addTo(map);
                    airportMarkers.addLayer(marker);
                    marker.bindPopup(`You: ${name}`);
                    marker.openPopup();
                } else {
                    marker = L.marker([latitude, longitude]).addTo(map);
                }

                // Attach a click event to each marker
                marker.on("click", (e) => {
                    console.log(`Clicked on ${name}`);
                    updateFlyProtocol(airport);
                });
            }
        }

        // Function to update Fly Protocol with airport information
        const updateFlyProtocol = (airport) => {
            const flyProtocol = document.querySelector("#flight-protocol");
            flyProtocol.innerHTML = `
                <h2>Fly Protocol</h2>
                <p>Airport Name: ${airport.name}</p>
                <p>Country: ${airport.country_name}</p>
                <p>Fuel: Unknown</p>
                <p>Money: Unknown</p>
                <p>CO2: unknown</p>
            `;
            // console.log(airport)
        };
    } catch (error) {
        // Handle the error (e.g., display an error message on the page)
        console.error(error.message);
    }
};

(() => {
    const gameID = getGameIdFromUrl();
    gameSetup(gameID);
})();
