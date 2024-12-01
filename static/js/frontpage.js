const postData = async (url, data) => {
    try {
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(data), // convert JavaScript object to JSON string
        })
        return await response.json()
    } catch (error) {
        console.error("Error:", error)
        return await error.json()
    }
}

const modal = document.getElementById('myModal')

// Function to open the modal
function openModal() {
    document.getElementById("playerName").value = ''
    modal.style.display = 'flex'
}

// Function to close the modal
function closeModal() {
    modal.style.display = 'none'
}

// Function to start a new game (you can modify this as needed)
const popupNameInput = () => {
    openModal()
}
// send post to create new game
document.getElementById("start-game").addEventListener("click", async () => {
    const url = "game/new-game"
    const name = document.getElementById("playerName").value
    const re = "^[\w'\-,.][^0-9_!¡?÷?¿/\\+=@#$%ˆ&*(){}|~<>;:[\]]{2,}$"
    const isValidName = /^[a-z ,.'-]+$/i.test(name)
    if (name){
        const data = { name: name }
        const response = await postData(url, data)
        const gameID = response.gameID
        console.log(`Game ID: ${gameID}`)
        window.location.href = `game/${gameID}`
    } else {
        alert('Please enter a valid name')
    }
})