// global variables
let currentAirportMarker;


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

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error("Error:", error);
        return await error.json();
    }
};

// function get game id
const getGameIdFromUrl = () => {
    const pathParts = window.location.pathname.split("/");
    return pathParts[pathParts.length - 1];
};


// function update player status
const updatePlayerStatus = async (pstatus) => {
    // const gameId = getGameIdFromUrl()

    // const status = await getData(`/game/${gameId}/get-player-data`);
    const name = document.getElementById("player-name");
    const time = document.getElementById("time-left");
    const money = document.getElementById("money");
    const fuel = document.getElementById("fuel");
    const emission = document.getElementById("co2-emission");
    const location = document.getElementById("location");

    name.innerText = `${pstatus.player.name}`;
    time.innerText = `${pstatus.player.time}`;
    money.innerText = `${pstatus.player.money}`;
    fuel.innerText = `${pstatus.player.fuel}`;
    emission.innerText = `${pstatus.player.emission}`;
    location.innerText = `${pstatus.player.location}`;
}

 // Function to update Fly Protocol with airport information
 const updateFlyProtocol = (airport) => {
    const flyProtocol = document.querySelector("#flight-protocol");
    
    flyProtocol.innerHTML = `
        <h2>Fly Protocol</h2>
        <p>ICAO code: ${airport.ident}</p>
        <p>Airport Name: ${airport.name}</p>
        <p>Country: ${airport.country_name}</p>
        <p>Fuel: ${airport.fuel ? airport.fuel : 0}</p>
        <p>Money: ${airport.reward ? airport.reward : 0}</p>
        <p>CO2: ${airport.emission ? airport.emission : 0}</p>
    `
};

// unload modal
const showOptionsModal = () => {
    const modal = document.getElementById('options-modal');
    if (modal) {
        modal.style.display = 'flex';
    }
};

const hideOptionsModal = () => {
    const modal = document.getElementById('options-modal');
    if (modal) {
        modal.style.display = 'none';
    }
};

// function check game finish
const isGameFinish = (pstatus) => {
    return pstatus.player.finish === 1 ? true : false
}



// main function to set up the game
const gameSetup = async (gameId) => {
    try {
        // function exit the game
        const exitIcon = document.querySelector('#exit');
        if (exitIcon) {
            exitIcon.addEventListener('click', function() {
                const userConfirmed = confirm('Do you want to exit the game?');
                if (userConfirmed) {
                    console.log('Exiting the game...');
                } else {
                    console.log('User canceled game exit.');
                }
            });
        } else {
            console.error('Exit button not found.');
        }


        const flyButton = document.querySelector('.fly')
        // console.log(flyButton)


        airportMarkers.clearLayers();
        const status = await getData(`/game/${gameId}/get-player-data`);
        updatePlayerStatus(status)


        const airportsData = await getData(`/game/${gameId}/get-airports-data`);
        const airports = airportsData.airports;
        let selectedAirport;

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
                    marker.bindPopup(`You are at ${name} airport`);
                    marker.openPopup();
                } else {
                    marker = L.marker([latitude, longitude]).addTo(map);
                }

                // Attach a click event to each marker
                marker.on("click", () => {
                    selectedAirport = airport;
                    updateFlyProtocol(airport);

                    // Check if the Fly button should be enabled
                    if (status.player.location === selectedAirport.ident) {
                        flyButton.disabled = true; // Disable the button
                        console.log('Player is already at the current airport. Fly button disabled.');
                    } else {
                        // Enable the button and attach the click event listener
                        flyButton.disabled = false;
                        flyButton.addEventListener('click', async function () {
                            try {
                                const jsonData = `{"ident": "${selectedAirport.ident}"}`;
                                await postData(`/game/${gameId}/fly`, jsonData);
                                gameSetup(gameId)
                                showOptionsModal();
                            } catch (error) {
                                console.error(error);
                            }
                        });
                    }
                });
            }
        }

        // Add event listeners for modal options (dice and unload)
        const diceOption = document.getElementById('dice-option');
        const unloadOption = document.getElementById('unload-option');

        diceOption.addEventListener('click', async () => {
            console.log('Dice option clicked');
            // try {
            //     const jsonData = {"option": "0"};
            //     await postData(`/game/${gameId}/unload`, jsonData);
            //     const updatedStatus = await getData(`/game/${gameId}/get-player-data`);
            //     console.log(updatedStatus)
            //     updatePlayerStatus(updatedStatus);
            //     hideOptionsModal();
            // } catch (error) {
            //     console.error(error);
            // }
        });

        unloadOption.addEventListener('click', async () => {
            console.log('Unload option clicked');
            try {
                const jsonData = { "option": "0" };
                await postData(`/game/${gameId}/unload`, jsonData);
        
                // Update player status after unloading
                // const updatedStatus = await getData(`/game/${gameId}/get-player-data`);
                // updatePlayerStatus(updatedStatus);
        
                // Check if the game is finished
                if (isGameFinish(updatedStatus)) {
                    // Display congratulations message or perform any other game-end logic
                    alert("Congratulations! The game has ended.");
                } else {
                    // Continue the game setup
                    gameSetup(gameId);
                }
                // Hide the options modal
                hideOptionsModal();
            } catch (error) {
                console.error(error);
            }
        });
        


    } catch (error) {
        // Handle the error (e.g., display an error message on the page)
        console.error(error.message);
    }
};

(() => {
    const gameID = getGameIdFromUrl();
    gameSetup(gameID);
})();
