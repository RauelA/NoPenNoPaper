document.addEventListener("DOMContentLoaded", () => {

    const storyText = document.getElementById("story-text");
    const form = document.getElementById("question-form");
    const input = document.getElementById("question-input");
    const submitBtn = document.getElementById("submit-btn");


    // Spiel starten
    startGame();



    async function startGame() {

        try {

            const response = await fetch("/api/start");

            const data = await response.json();

            storyText.textContent = data.scene;


        } catch(error) {

            console.error(error);

            storyText.textContent =
                "Die Welt konnte nicht erschaffen werden.";

        }
    }



    form.addEventListener("submit", async (event)=>{

    event.preventDefault();


    const action = input.value;


    const response = await fetch(
        "/api/action",
        {
            method:"POST",
            headers:{
                "Content-Type":"application/json"
            },
            body:JSON.stringify({
                action: action
            })
        }
    );


    const data = await response.json();


    document.getElementById(
        "story-text"
    ).textContent = data.scene;


    input.value="";

});


});