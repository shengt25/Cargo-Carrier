//------------------------------
//  Global Variables
//------------------------------
class GlobalData {
    constructor() {
        this.selectedAirport = null;
        this.airportsData = null;
        this.playerData = null;
        this.gameID = null;
    }
}

const globalData = new GlobalData();

//------------------------------
//  BASIC POST AND GET FUNCTIONS
//------------------------------

async function getData(url) {
    const response = await fetch(url);
    if (!response.ok) throw new Error("Invalid server input");
    return await response.json();
}

async function postData(url, data) {
    const response = await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(data), // convert JavaScript object to JSON string
    });
    if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
    return await response.json();
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

    // event listeners for panel buttons shop, map, hall
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
            shopDialogueTextContainer.style.display = "inline";
        }, 500);

        // display dialogues in shop
        document.getElementById("shop-dialogue-text").innerText =
            `Welcome to the shop, ${globalData.playerData.name}!` +
            "\nWhat do you want to buy today?";
        if (globalData.playerData.home === globalData.playerData.location) {
            document.getElementById("shop-item-airport").style.display = "flex";
        } else {
            document.getElementById("shop-item-airport").style.display = "none";
        }
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
            hallDialogueTextContainer.style.display = "inline";
        }, 500);

        // display dialogues in hall, and options if player has cargo
        const hasCargo = globalData.playerData.has_cargo;
        console.log("hall button hit, does player has cargo? " + hasCargo);
        if (hasCargo) {
            // show unload options
            hallBoardContainer.style.display = "flex";
            setTimeout(() => {
                hallItemContainer.style.display = "flex";
            }, 500);
            document.getElementById("hall-dialogue-text").innerText =
                "Now you need to unload the cargo, two choices:" +
                "\n\nI. Do it yourself: random event will happen." +
                "\nII. Hire someone: €600. No risk, no reward.";
        }
    });
}

//------------------------------
//  UPDATE STATUS FUNCTIONS
//------------------------------

function initGlobalPlayerStatus() {
    globalData.playerData = {
        name: "",
        time: 0,
        money: 0,
        fuel: 0,
        emission: 0,
        home: "",
    };
}

function animateNumber(elementId, start, end, duration) {
    const range = end - start;
    const startTime = new Date().getTime(); // start time
    const timer = setInterval(function () {
        const now = new Date().getTime(); //  current time
        const elapsed = now - startTime; // how much time has elapsed
        const progress = Math.min(elapsed / duration, 1); // calculate progress
        document.getElementById(elementId).textContent =
            start + Math.round(range * progress);
        if (progress === 1) {
            // stop timer when exceed duration
            clearInterval(timer);
        }
    }, 20); // update every 20ms
}

async function updatePlayerStatus(gameID) {
    const playerResponse = await getData(`/game/${gameID}/get-player-data`);
    const oldPlayerData = globalData.playerData;
    const playerData = playerResponse.player;
    const name = document.getElementById("status-name");
    name.innerText = `${playerData.name}`;
    const duration = 1000;
    animateNumber("status-time", oldPlayerData.time, playerData.time, duration);
    animateNumber(
        "status-money",
        oldPlayerData.money,
        playerData.money,
        duration,
    );
    animateNumber("status-fuel", oldPlayerData.fuel, playerData.fuel, duration);
    animateNumber(
        "status-emission",
        oldPlayerData.emission,
        playerData.emission,
        duration,
    );
    return playerData;
}

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

async function isGameFinish() {
    const response = await getData(`/game/${globalData.gameID}/check-ending`);
    const isEnd = response["end"];
    console.log("is game end? " + isEnd);
    if (isEnd) {
        console.log("game ends, lose");
        // disable all panel buttons
        document.getElementById("btn-shop").disabled = true;
        document.getElementById("btn-map").disabled = true;
        document.getElementById("btn-hall").disabled = true;

        const endType = response["type"];
        if (endType === "time") {
            // out of time
            document.getElementById("hall-dialogue-text").innerText =
                "Sorry, you run out of time...\n Game over.";
        } else if (endType === "money") {
            // out of money
            document.getElementById("hall-dialogue-text").innerText =
                "Sorry, you run out of money...\n Game over.";
        }
    }
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
    // event listener will update fly protocol and fly button disabled status
    let airportMarker;
    const homeIcon = L.icon({
        iconUrl: "../static/img/marker-home.png",
        iconSize: [35, 35],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
    });
    if (airportData.ident === globalData.playerData.home) {
        // add home marker
        airportMarker = L.marker(
            [airportData.latitude_deg, airportData.longitude_deg],
            { icon: homeIcon },
        ).addTo(airportMarkerGroup);
        airportMarker.bindTooltip(
            `<h2>${airportData.country_name}</h2><p>${airportData.name} <b>(${airportData.ident})</b></p><p>This is your home</p>`,
        );
    } else {
        airportMarker = L.marker(
            [airportData.latitude_deg, airportData.longitude_deg],
            { icon: iconType },
        ).addTo(airportMarkerGroup);
        airportMarker.bindTooltip(
            `<h2>${airportData.country_name}</h2><p>${airportData.name} <b>(${airportData.ident})</b></p>`,
        );
    }

    airportMarker.on("click", () => {
        console.log(airportData);
        document.getElementById("btn-fly").disabled = isDisabled;
        document.getElementById("stamp").style.display = "none";
        updateFlyProtocol(airportData);
        globalData.selectedAirport = airportData;
    });
}

async function updateMap(gameID, map, airportMarkerGroup) {
    // get new airports data from server
    // clear layers
    // new markers with different colors
    // add event listeners to each marker
    console.log("updating map");
    const airportsResponse = await getData(`/game/${gameID}/get-airports-data`);
    const airportsData = airportsResponse.airports;

    const greenIcon = L.icon({
        iconUrl: "../static/img/marker-green.png",
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
    });
    // out range airports
    const redIcon = L.icon({
        iconUrl: "../static/img/marker-red.png",
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
    });
    const currentIcon = L.icon({
        iconUrl: "../static/img/marker-plane.png",
        iconSize: [35, 35],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
    });

    airportMarkerGroup.clearLayers();
    Object.keys(airportsData).forEach((ident) => {
        const airportData = airportsData[ident];
        const range_fuel = airportData.range_fuel;
        const range_time = airportData.range_time;

        // whether disable the marker or not
        if (airportData.current === true) {
            addMarker(currentIcon, airportMarkerGroup, airportData, true);
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
//  BUY BUTTON EVENT CALLBACKS
//------------------------------
async function buyCallback(item) {
    let amount;
    let inputElem;
    if (item === "fuel") {
        inputElem = document.getElementById("shop-item-fuel-input");
        amount = inputElem.value;
        inputElem.value = "";
    } else if (item === "coffee") {
        inputElem = document.getElementById("shop-item-coffee-input");
        amount = inputElem.value;
        inputElem.value = "";
    } else if (item === "airport") {
        amount = 1;
    } else {
        // other items not implemented yet
        amount = 0;
    }

    const dialogText = document.getElementById("shop-dialogue-text");
    let isNum = /^\d+$/.test(amount);
    if (!isNum) {
        // fail: not number
        dialogText.innerText = "Hmm, sorry but...\n What is it again, please?";
    } else {
        const response = await postData(`/game/${globalData.gameID}/buy`, {
            item: item,
            amount: amount,
        });
        if (response.success) {
            // ok: response success
            globalData.playerData = await updatePlayerStatus(globalData.gameID);

            // fuel is special, because the amount is money not items amount
            if (item === "fuel")
                dialogText.innerText = `Thank you! 
                You just bought ${response.amount} ton fuel with € ${amount}.`;
            else if (item === "airport") {
                // win!!!
                dialogText.innerText = `Congratulations ${globalData.playerData.name}! Finally you made it!`;
            }
            // other countable items
            else
                dialogText.innerText = `Thank you! 
                You just bought ${response.amount} ${item}.`;
        } else if (response.reason === "money") {
            // fail: not enough money
            dialogText.innerText = "Sorry, you don't have enough money.";
        } else {
            // fail: other reasons, show message
            dialogText.innerText = response.message;
        }
    }
}

(async () => {
    //------------------------------
    //   SET EVENT LISTENERS
    //------------------------------
    // NOTE: in click events, game data should also be updated to globalData

    // buy fuel button listener
    document
        .getElementById("shop-item-fuel-btn")
        .addEventListener("click", async () => buyCallback("fuel"));

    // buy fuel coffee listener
    document
        .getElementById("shop-item-coffee-btn")
        .addEventListener("click", async () => buyCallback("coffee"));

    // buy airport button listener
    document
        .getElementById("shop-item-airport-btn")
        .addEventListener("click", async () => buyCallback("airport"));

    // fly button listener
    document
        .getElementById("btn-fly")
        .addEventListener("click", async (event) => {
            // jump to hall if player has cargo
            if (globalData.playerData.has_cargo) {
                document.getElementById("btn-hall").click();
                document.getElementById("hall-dialogue-text").innerText =
                    "Eh... You still have cargo, can't fly now. \nSo... please make your choice.";
            }

            if (globalData.selectedAirport) {
                try {
                    // fly and get new data
                    const jsonData = {
                        ident: globalData.selectedAirport.ident,
                    };
                    const response = await postData(
                        `/game/${gameID}/fly`,
                        jsonData,
                    );
                    if (response.success) {
                        globalData.airportsData = await updateMap(
                            gameID,
                            map,
                            airportMarkerGroup,
                        );
                        globalData.playerData =
                            await updatePlayerStatus(gameID);
                        // disable fly button
                        globalData.selectedAirport = null;
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

    // hire button listener
    document
        .getElementById("hall-item-hire-btn")
        .addEventListener("click", async (event) => {
            try {
                const jsonData = { option: 0 };
                const response = await postData(
                    `/game/${gameID}/unload`,
                    jsonData,
                );
                if (response.success) {
                    // make sure disabled fly button
                    document.getElementById("btn-fly").disabled = true;

                    // if success, update player status
                    globalData.playerData = await updatePlayerStatus(gameID);

                    // hide options
                    document.getElementById(
                        "hall-board-container",
                    ).style.display = "none";
                    document.getElementById(
                        "hall-item-container",
                    ).style.display = "none";
                    document.getElementById("hall-dialogue-text").innerText =
                        "Great, you made a wise choice! \nOnly cost you € 600, hehehe...";
                } else if (response.reason === "money") {
                    document.getElementById("hall-dialogue-text").innerText =
                        "Hmm, maybe you wanna do it yourself? \nBecause you don't have enough money.";
                } else {
                    // unexpected reason
                    document.getElementById("hall-dialogue-text").innerText =
                        response.message;
                }
                // check if game is ends
                void isGameFinish();
                void updateMap(gameID, map, airportMarkerGroup);
            } catch (error) {
                console.error(error);
            }
        });

    // dice button listener
    document
        .getElementById("hall-item-dice-btn")
        .addEventListener("click", async (event) => {
            try {
                const jsonData = { option: 1 };
                const response = await postData(
                    `/game/${gameID}/unload`,
                    jsonData,
                );
                if (response.success) {
                    // make sure disabled fly button
                    document.getElementById("btn-fly").disabled = true;

                    // if success, update player status
                    globalData.playerData = await updatePlayerStatus(gameID);
                    // enable fly button
                    document.getElementById("btn-fly").disabled = false;
                    // hide options
                    document.getElementById(
                        "hall-board-container",
                    ).style.display = "none";
                    document.getElementById(
                        "hall-item-container",
                    ).style.display = "none";
                    let diceMessage = "";
                    switch (response.dice) {
                        case 1:
                            diceMessage =
                                "Oh no! Your competitor secretly broke your precious cargo, " +
                                "that cost 90% of your deposit!";
                            break;
                        case 2:
                            diceMessage =
                                "The cargo is heavily damaged. \nYou lost € 1500!";
                            break;
                        case 3:
                            diceMessage =
                                "Well, things go smoothly. \nNothing happened to you.";
                            break;
                        case 4:
                            diceMessage =
                                "Wow! You did a great job. \nYou earned extra € 1500!";
                            break;
                        case 5:
                            diceMessage =
                                "Congratulation!!! \nYou get a SUPER BIG tip for € 1800!";
                            break;
                        case 6:
                            diceMessage =
                                "What a lucky day! \nYour money doubled!";
                            break;
                    }
                    document.getElementById("hall-dialogue-text").innerText =
                        diceMessage;
                } else {
                    // unexpected reason
                    document.getElementById("hall-dialogue-text").innerText =
                        response.message;
                }
                // check if game is ends
                void isGameFinish();
                void updateMap(gameID, map, airportMarkerGroup);
            } catch (error) {
                console.error(error);
            }
        });

    // power off button listener
    document.getElementById("shutdown").addEventListener("click", () => {
        const userConfirmed = confirm("Do you want to exit the game?");
        if (userConfirmed) {
            console.log("Exiting the game...");
        } else {
            console.log("User canceled game exit.");
        }
    });

    //------------------------------
    //   INIT GAME
    //------------------------------
    // init panel button
    initPanelButton();

    // have to display map first, otherwise map will not be setup correctly
    document.getElementById("map").style.display = "flex";
    const gameID = getGameIDFromUrl();
    const [map, airportMarkerGroup] = initMap();
    globalData.gameID = gameID;

    // init player status
    initGlobalPlayerStatus();

    // wait 500ms and start new game in hall
    setTimeout(async () => {
        // update player status
        globalData.playerData = await updatePlayerStatus(gameID);
        globalData.airportsData = await updateMap(
            gameID,
            map,
            airportMarkerGroup,
        );
        document.getElementById(
            "hall-dialogue-text",
        ).innerText = `Good morning ${globalData.playerData.name}, Welcome!\nYour goal is to earn €20 000 in 10 days. Ready to start? Good luck!`;

        document.getElementById("btn-hall").click();
    }, 500);
})();
