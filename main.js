// initialize the map
const map = L.map("map", { tap: false });

const airportMarkers = L.featureGroup().addTo(map);
// add map
L.tileLayer("https://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}", {
  maxZoom: 20,
  subdomains: ["mt0", "mt1", "mt2", "mt3"],
}).addTo(map);
map.setView([60, 50], 3);
// map.invalidateSize();

document.getElementById("btn-shop").addEventListener("click", (e) => {
  const map = document.getElementById("map");
  const shop = document.getElementById("shop");
  const hall = document.getElementById("hall");
  shop.style.display = "block";
  map.style.display = "none";
  hall.style.display = "none";

  setTimeout(function() {
    shop.style.filter = "blur(10px)";
  }, 500);
  hall.style.filter = "none";
});

document.getElementById("btn-map").addEventListener("click", (e) => {
  const map = document.getElementById("map");
  const shop = document.getElementById("shop");
  const hall = document.getElementById("hall");
  map.style.display = "block";
  shop.style.display = "none";
  hall.style.display = "none";
  hall.style.filter = "none";
  shop.style.filter = "none";
});

document.getElementById("btn-hall").addEventListener("click", (e) => {
  const map = document.getElementById("map");
  const shop = document.getElementById("shop");
  const hall = document.getElementById("hall");
  hall.style.display = "block";
  map.style.display = "none";
  shop.style.display = "none";

  setTimeout(function() {
    hall.style.filter = "blur(10px)";
  }, 500);
  shop.style.filter = "none";
});

document.getElementById("btn-fly").addEventListener("click", (e) => {
    const stamp = document.getElementById("stamp");
    stamp.style.display = "block";

});