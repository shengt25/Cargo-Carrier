//------------------------------
//  Global Variables
//------------------------------
let selectedAirport;
let airportsData;
let playerData;

//------------------------------
//  BASIC POST AND GET FUNCTIONS
//------------------------------

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

//------------------------------
//  INIT WEBPAGE PANEL BUTTON STYLE CHANGE (too long and duplicated, need to tidy it up in the future...)
//------------------------------
function initPanelButton() {
    const shopDiv = document.getElementById("shopDiv");
    const hallDiv = document.getElementById("hallDiv");
    const mapDiv = document.getElementById("map");
    const shopMainBackground = document.getElementById("shop-main-background");
    const hallMainBackground = document.getElementById("hall-main-background");
    const shopBoardContainer = document.getElementById("shop-board-container");
    const hallBoardContainer = document.getElementById("hall-board-container");
    const shopItemContainer = document.getElementById("shop-item-container");
    const hallItemContainer = document.getElementById("hall-item-container");
    const shopDialogueBubble = document.getElementById("shop-dialogue-bubble");
    const hallDialogueBubble = document.getElementById("hall-dialogue-bubble");
    const shopDialogueTextContainer = document.getElementById(
        "shop-dialogue-text-container",
    );
    const hallDialogueTextContainer = document.getElementById(
        "hall-dialogue-text-container",
    );
    const btnShop = document.getElementById("btn-shop");
    const btnMap = document.getElementById("btn-map");
    const btnHall = document.getElementById("btn-hall");

    shopDiv.style.display = "none";
    mapDiv.style.display = "none";

    document.getElementById("btn-shop").addEventListener("click", (e) => {
        btnShop.classList.remove("btn");
        btnShop.classList.add("btn-pressed");
        btnMap.classList.remove("btn-pressed");
        btnMap.classList.add("btn");
        btnHall.classList.remove("btn-pressed");
        btnHall.classList.add("btn");

        shopDiv.style.display = "flex";
        shopBoardContainer.style.display = "flex";
        shopDialogueBubble.style.display = "flex";

        mapDiv.style.display = "none";
        hallDiv.style.display = "none";
        hallItemContainer.style.display = "none";
        hallMainBackground.style.filter = "none";
        hallDialogueBubble.style.display = "none";
        hallDialogueTextContainer.style.display = "none";

        setTimeout(() => {
            shopMainBackground.style.filter = "blur(10px)";
        }, 500);
        setTimeout(() => {
            shopItemContainer.style.display = "flex";
        }, 500);
        setTimeout(() => {
            shopDialogueTextContainer.style.display = "flex";
        }, 500);
    });

    document.getElementById("btn-map").addEventListener("click", (e) => {
        btnShop.classList.remove("btn-pressed");
        btnShop.classList.add("btn");
        btnMap.classList.remove("btn");
        btnMap.classList.add("btn-pressed");
        btnHall.classList.remove("btn-pressed");
        btnHall.classList.add("btn");

        mapDiv.style.display = "flex";

        shopDiv.style.display = "none";
        hallDiv.style.display = "none";
        shopBoardContainer.style.display = "none";
        hallBoardContainer.style.display = "none";
        shopDialogueBubble.style.display = "none";
        hallDialogueBubble.style.display = "none";
        shopItemContainer.style.display = "none";
        hallItemContainer.style.display = "none";
        shopDialogueTextContainer.style.display = "none";
        hallDialogueTextContainer.style.display = "none";

        hallMainBackground.style.filter = "none";
        shopMainBackground.style.filter = "none";
    });

    document.getElementById("btn-hall").addEventListener("click", (e) => {
        btnShop.classList.remove("btn-pressed");
        btnShop.classList.add("btn");
        btnMap.classList.remove("btn-pressed");
        btnMap.classList.add("btn");
        btnHall.classList.remove("btn");
        btnHall.classList.add("btn-pressed");

        hallDiv.style.display = "flex";

        mapDiv.style.display = "none";
        shopDiv.style.display = "none";
        shopDialogueBubble.style.display = "none";
        hallDialogueBubble.style.display = "flex";
        shopMainBackground.style.filter = "none";
        shopItemContainer.style.display = "none";
        shopDialogueTextContainer.style.display = "none";

        setTimeout(() => {
            hallMainBackground.style.filter = "blur(10px)";
        }, 500);

        setTimeout(() => {
            hallDialogueTextContainer.style.display = "flex";
        }, 500);

        const hasCargo = playerData.cargo !== null;

        if (hasCargo) {
            hallBoardContainer.style.display = "flex";
            setTimeout(() => {
                hallItemContainer.style.display = "flex";
            }, 500);
            document.getElementById("hall-dialogue-text").innerText =
                "Now you need to unload the cargo, two choices: I. Do it yourself: a dice game will decide your fate. II. Hire someone: €600, no risk no reward.";
            // show unload options
            document.getElementById("hall-board-container").style.display =
                "flex";
            document.getElementById("hall-item-container").style.display =
                "flex";
        }
    });
}

//------------------------------
//  UPDATE STATUS FUNCTIONS
//------------------------------

const updatePlayerStatus = async (gameID) => {
    const playerResponse = await getData(`/game/${gameID}/get-player-data`);
    const playerData = playerResponse.player;
    const name = document.getElementById("status-name");
    const time = document.getElementById("status-time");
    const money = document.getElementById("status-money");
    const fuel = document.getElementById("status-fuel");
    const emission = document.getElementById("status-emission");

    name.innerText = `${playerData.name}`;
    time.innerText = `${playerData.time}`;
    money.innerText = `${playerData.money}`;
    fuel.innerText = `${playerData.fuel}`;
    emission.innerText = `${playerData.emission}`;
    return playerData;
};

function updateFlyProtocol(airportData) {
    const countryName = document.getElementById("flight-country-name");
    const airportName = document.getElementById("flight-airport-name");
    const fuel = document.getElementById("flight-fuel");
    const time = document.getElementById("flight-time");
    const emission = document.getElementById("flight-emission");
    const reward = document.getElementById("flight-reward");
    if (airportData.current === true) {
        countryName.innerText = `${airportData.country_name}`;
        airportName.innerText = `${airportData.name}`;
        fuel.innerText = "You are here";
        time.innerText = "";
        emission.innerText = "";
        reward.innerText = "";
    } else {
        countryName.innerText = `${airportData.country_name}`;
        airportName.innerText = `${airportData.name}`;
        fuel.innerText = `Fuel: ${airportData.fuel} ton`;
        time.innerText = `Time: ${airportData.time} hours`;
        emission.innerText = `Emission: ${airportData.emission} kg`;
        reward.innerText = `Reward: ${airportData.reward} €`;
    }
}

function isGameFinish(playerData) {
    return playerData.finish === 1;
}

//------------------------------
//  MAP FUNCTIONS
//------------------------------

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

function addMarker(iconType, airportMarkerGroup, airportData, isDisabled) {
    // add marker to map
    // add event listener to marker
    // event listener will update fly protocol and fly button
    const airportMarker = L.marker(
        [airportData.latitude_deg, airportData.longitude_deg],
        { icon: iconType },
    ).addTo(airportMarkerGroup);
    airportMarker.bindTooltip(
        `<h2>${airportData.country_name}</h2><p>${airportData.name} <b>(${airportData.ident})</b></p>`,
    );
    airportMarker.on("click", () => {
        console.log(airportData);
        document.getElementById("btn-fly").disabled = isDisabled;
        document.getElementById("stamp").style.display = "none";
        updateFlyProtocol(airportData);
        selectedAirport = airportData;
    });
}

async function updateMap(gameID, map, airportMarkerGroup) {
    // get new airports data from server
    // clear layers
    // new markers with different colors
    // add event listeners to each marker
    console.log("updating map");
    const airportsResponse = await getData(`/game/${gameID}/get-airports-data`);
    airportsData = airportsResponse.airports;

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
        const range_fuel = airportData.range_fuel;
        const range_time = airportData.range_time;
        if (airportData.current === true) {
            addMarker(redIcon, airportMarkerGroup, airportData, true);
        } else if (range_fuel === false || range_time === false) {
            console.log("out range");
            addMarker(redIcon, airportMarkerGroup, airportData, true);
        } else {
            addMarker(greenIcon, airportMarkerGroup, airportData, false);
        }
    });
    map.fitBounds(airportMarkerGroup.getBounds());
    return airportsData;
}

//------------------------------
//  SHOP FUNCTIONS
//------------------------------

//------------------------------
//   HALL FUNCTIONS
//------------------------------

(async () => {
    //------------------------------
    //   SET EVENT LISTENERS
    //------------------------------

    // Hire, Myself, Fly buttons
    // const btnHire = document.getElementById("dice-option");
    // const btnMyself = document.getElementById("unload-option");
    const btnFly = document.getElementById("btn-fly");

    // btnMyself.addEventListener("click", async () => {
    //     try {
    //         const jsonData = { option: 1 };
    //         await postData(`/game/${gameID}/unload`, jsonData);
    //         updateMap(gameID, map, airportMarkerGroup);
    //         updatePlayerStatus(gameID);
    //         hideOptionsModal();
    //     } catch (error) {
    //         console.error(error);
    //     }
    // });
    //
    // btnHire.addEventListener("click", async () => {
    //     try {
    //         const jsonData = { option: 0 };
    //         await postData(`/game/${gameID}/unload`, jsonData);
    //         updateMap(gameID, map, airportMarkerGroup);
    //         updatePlayerStatus(gameID);
    //         hideOptionsModal();
    //     } catch (error) {
    //         console.error(error);
    //     }
    // });

    btnFly.addEventListener("click", async (event) => {
        if (selectedAirport) {
            try {
                // fly and get new data
                const jsonData = { ident: selectedAirport.ident };
                const response = await postData(
                    `/game/${gameID}/fly`,
                    jsonData,
                );
                if (response.success) {
                    airportsData = await updateMap(
                        gameID,
                        map,
                        airportMarkerGroup,
                    );
                    playerData = await updatePlayerStatus(gameID);
                    // disable fly button
                    selectedAirport = null;
                    event.target.disabled = true;
                    // show stamp
                    const stamp = document.getElementById("stamp");
                    stamp.style.display = "block";
                    // go to hall
                    document.getElementById("btn-hall").click();
                }
            } catch (error) {
                console.error(error);
            }
        }
    });

    //------------------------------
    //   INIT GAME
    //------------------------------
    initPanelButton();
    const gameID = getGameIDFromUrl();
    const [map, airportMarkerGroup] = initMap();
    airportsData = await updateMap(gameID, map, airportMarkerGroup);
    playerData = await updatePlayerStatus(gameID);

    // start new game in hall
    // document.getElementById(
    //     "hall-dialogue-text",
    // ).innerText = `Nice to meet you, ${playerData.name} ! Your goal is to buy your own airport (€20 000) in 10 days, good luck!`;
    // document.getElementById("btn-hall").click();
})();
