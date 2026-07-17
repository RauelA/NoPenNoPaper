document.addEventListener("DOMContentLoaded", () => {

    const storyText = document.getElementById("story-text");
    const form = document.getElementById("question-form");
    const input = document.getElementById("question-input");
    const submitBtn = document.getElementById("submit-btn");


    // Spiel starten
    document.getElementById("start-btn").addEventListener("click", startGame);

    const translations = {

        de: {
            universe: "Universum / Genre",
            player: "Spieler",
            universePlaceholder:
                "Beschreibe das Universum und dessen Eigenschaften.",
            playerPlaceholder:
                "Beschreibe dich und deine Fähigkeiten.",
            loading:
                "Welt wird erschaffen...",
            action:
                "Was tust du?",
            start:
                "Start"
        },

        en: {
            universe: "Universe / Genre",
            player: "Player",
            universePlaceholder:
                "Describe the universe and its properties.",
            playerPlaceholder:
                "Describe yourself and your abilities.",
            loading:
                "Creating world...",
            action:
                "What do you do?",
            start:
                "Start"
        },

        zh: {
            universe: "宇宙 / 类型",
            player: "玩家",
            universePlaceholder:
                "描述这个宇宙及其特点。",
            playerPlaceholder:
                "描述你自己以及你的能力。",
            loading:
                "正在创造世界...",
            action:
                "你要做什么？",
            start:
                "开始"
        }

    };

    const languageSelect =
    document.getElementById("language-select");

    languageSelect.addEventListener(
        "change",
        updateLanguage
    );

    updateLanguage();


    function updateLanguage(){

        const lang =
            translations[languageSelect.value];

        document.getElementById("universe-title").textContent =
            lang.universe;

        document.getElementById("player-title").textContent =
            lang.player;

        document.getElementById("universe-input").placeholder =
            lang.universePlaceholder;

        document.getElementById("player-input").placeholder =
            lang.playerPlaceholder;

        document.getElementById("question-input").placeholder =
            lang.action;

        document.getElementById("story-text").textContent =
            lang.loading;

    }

    async function startGame(){

        const startBtn = document.getElementById("start-btn");

            startBtn.disabled = true;
            startBtn.textContent = "...";

        const language =
            languageSelect.value;

        const universe =
            document.getElementById("universe-input").value;

        const player =
            document.getElementById("player-input").value;

        const response = await fetch("/api/start",{

            method:"POST",

            headers:{
                "Content-Type":"application/json"
            },

            body:JSON.stringify({

                language:language,

                universe:universe,

                player:player

            })

        });

        const data = await response.json();

        storyText.textContent = data.scene;

        document
            .getElementById("setup-screen")
            .classList.add("hidden");

        document
            .getElementById("game-screen")
            .classList.remove("hidden");
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