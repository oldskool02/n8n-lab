const servingsSelect = document.getElementById("servings");
const dietSelect = document.getElementById("diet");
const cuisineSelect = document.getElementById("cuisine");
const generateForm = document.getElementById("generate-form");
const requestInput = document.getElementById("request");
const validationMessage = document.getElementById("validation-message");
const generateButton = document.getElementById("generate-button");

let selectedRecipeId = null;

const errorPopup = document.getElementById("error-popup");
const errorPopupMessage = document.getElementById("error-popup-message");
const errorPopupOk = document.getElementById("error-popup-ok");


errorPopupOk.addEventListener("click", function() {
    errorPopup.hidden = true;
});

function startNewGeneration() {
    selectedRecipeId = null;

    generateForm.reset();

    servingsSelect.value = "2";
    dietSelect.value = "";
    cuisineSelect.value = "";

    validationMessage.textContent = "";

    document
        .querySelectorAll(".recipe-list-item")
        .forEach(item => {
            item.classList.remove("selected");
        });

    document.getElementById("recipe-view").innerHTML = `
        <div class="empty-state">
            <h2>No Recipe Selected</h2>
            <p>Generate a recipe or select one from My Recipes.</p>
        </div>
    `;

    generateButton.textContent = "Generate";

}

function showErrorPopup(message) {
    errorPopupMessage.textContent = message;
    errorPopup.hidden = false;
}

const loginPassword = document.getElementById("login-password");
const showPassword = document.getElementById("show-password");

const loginForm = document.getElementById("login-form");
const loginEmail = document.getElementById("login-email");
const loginMessage = document.getElementById("login-message");

const loginView = document.getElementById("login-view");
const appView = document.getElementById("app-view");



/*
* Show Password
*/
showPassword.addEventListener("change", function() {
    loginPassword.type = showPassword.checked
        ? "text"
        : "password";
});

loginForm.addEventListener("submit", async function (event) {
    event.preventDefault();


    loginMessage.textContent = "";
    loginMessage.style.color = "";

    const email = loginEmail.value.trim();
    const password = loginPassword.value;

    try {
        const response = await fetch(
            "http://localhost:8001/users/login",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    email: email,
                    password: password,
                }),
            }
        );

        if (!response.ok) {
            loginMessage.textContent =
                "Invalid email or password.";

            loginMessage.style.color = "red";

            return;
        }

        const data = await response.json();

        sessionStorage.setItem(
            "access_token",
            data.access_token
        );

        sessionStorage.setItem(
            "refresh_token",
            data.refresh_token
        );

        loginView.hidden = true;
        appView.hidden = false;

        await loadRecipes();

    } catch (error) {
        console.error(error);

        loginMessage.textContent =
            "Could not connect to the server.";

        loginMessage.style.color = "red";
    }
});

/*
 * Servings
 */

for (let servings = 1; servings <= 100; servings++) {
    const option = document.createElement("option");

    option.value = servings;
    option.textContent = servings;

    if (servings === 2) {
        option.selected = true;
    }

    servingsSelect.appendChild(option);
}


/*
 * Diet options
 */

const diets = [
    "None",
    "Vegetarian",
    "Vegan",
    "Gluten-Free",
    "Dairy-Free",
];

for (const diet of diets) {
    const option = document.createElement("option");

    option.value = diet === "None" ? "" : diet;
    option.textContent = diet;

    dietSelect.appendChild(option);
}


/*
 * Cuisine options
 */

const cuisines = [
    "None",
    "Italian",
    "French",
    "Indian",
    "Chinese",
    "Mexican",
    "Thai",
    "Mediterranean",
];

for (const cuisine of cuisines) {
    const option = document.createElement("option");

    option.value = cuisine === "None" ? "" : cuisine;
    option.textContent = cuisine;

    cuisineSelect.appendChild(option);
}


/*
 * Basic recipe request validation
 */

generateForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    validationMessage.textContent = "";
    validationMessage.style.color = "";

    const request = requestInput.value.trim();
    const servings = Number(servingsSelect.value);

    if (!request) {
        showErrorPopup(
            "Please enter a recipe request"
        );

        requestInput.focus();

        return;
    }

    if (servings < 1 || servings > 100) {
        validationMessage.textContent =
            "Servings must be between 1 and 100.";

        validationMessage.style.color = "red";
        servingsSelect.focus();

        return;
    }

    const accessToken = sessionStorage.getItem("access_token");

    if (!accessToken) {
        validationMessage.textContent =
            "Please log in again.";

        validationMessage.style.color = "red";

        return;
    }

    generateButton.disabled = true;

    validationMessage.textContent = "Generating recipe...";
    validationMessage.style.color = "green";

    try {
        const response = await fetch(
            "http://localhost:8001/recipes/generate",
            {
                method: "POST",
                headers: {
                    "Authorization": `Bearer ${accessToken}`,
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    request: request,
                    servings: servings,
                    dish: document.getElementById("dish").value.trim() || null,
                    diet: dietSelect.value || null,
                    cuisine: cuisineSelect.value || null,
                }),
            }
        );

        if (!response.ok) {
            let message = "Could not generate the recipe.";

            try {
                const errorData = await response.json();

                if (errorData.detail) {
                    message = errorData.detail;
                }
            } catch (error) {
                console.error("Could not read error response", error);
            }

            validationMessage.textContent = message;
            validationMessage.style.color = "red";

            generateForm.reset();

            servingsSelect.value = 2;
            dietSelect.value = "";
            cuisineSelect.value = "";

            return;
        }

        const recipe = await response.json();

        console.log("Generated recipe:", recipe);

        selectedRecipeId = recipe.id;

        displayRecipes(recipe);

        try {
            await loadRecipes();
        } catch (error) {
            console.error("Loading My Recipes failed", error)
        }

        generateForm.reset();

        servingsSelect.value = "2";
        dietSelect.value = "";
        cuisineSelect.value = "";

        validationMessage.textContent = "Recipe generated successfully.";
        validationMessage.style.color = "green";
    } catch (error) {
        console.error("Recipe generation failed:", error);

        validationMessage.textContent = "Could not connect to the server.";
        validationMessage.style.color = "red";
    } finally {
        generateButton.disabled = false
    }

});

generateButton.addEventListener("click", function(event) {
    if (selectedRecipeId !== null) {
        event.preventDefault();
        startNewGeneration();
    }
});

function displayRecipes(recipe) {
    const recipeView = document.getElementById("recipe-view");

    selectedRecipeId = recipe.id;

    generateButton.textContent = "New Generation";

    recipeView.innerHTML = "";

    const imagePlaceholder = document.createElement("div");
    imagePlaceholder.className = "recipe-image-placeholder";
    imagePlaceholder.textContent = "Recipe Image";
    recipeView.appendChild(imagePlaceholder);

    const title = document.createElement("h2");
    title.textContent = recipe.title;
    recipeView.appendChild(title);

    const servings = document.createElement("p");
    servings.textContent = `Servings: ${recipe.servings}`;
    recipeView.appendChild(servings);

    const ingredientsHeading = document.createElement("h3");
    ingredientsHeading.textContent = "Ingredients";
    recipeView.appendChild(ingredientsHeading);

    const ingredientsList = document.createElement("ul");

    for (const item of recipe.ingredients) {
        const ingredientItem = document.createElement("li");

        const quantity = item.quantity || "";
        const unit = item.unit || "";
        const ingredient = item.ingredient || "";

        ingredientItem.textContent = `${quantity} ${unit} ${ingredient}`.trim();

        ingredientsList.appendChild(ingredientItem);
    }

    recipeView.appendChild(ingredientsList);

    const stepHeading = document.createElement("h3");
    stepHeading.textContent = "Method";
    recipeView.appendChild(stepHeading);

    const stepsList = document.createElement("ol");

    for (const step of recipe.steps) {
        const stepItem = document.createElement("li");

        stepItem.textContent = step.instruction;

        stepsList.appendChild(stepItem);
    }

    recipeView.appendChild(stepsList);

}

async function loadRecipes() {
    const accessToken = sessionStorage.getItem("access_token");

    if (!accessToken) {
        return;
    }

    try {
        const response = await fetch(
            "http://localhost:8001/recipes/",
            {
                method: "GET",
                headers: {
                    "Authorization": `Bearer ${accessToken}`,
                },
            }
        );

        if (!response.ok) {
            console.error(
                "Could not load the recipes",
                response.status
            );

            if (response.status === 401) {
                return false;
            }

            return;
        }

        const recipes = await response.json();

        const recipesContainer = document.getElementById("recipes");

        recipesContainer.innerHTML = "";

        for (const recipe of recipes) {
            const recipeItem = document.createElement("button");

            recipeItem.type = "button";
            recipeItem.className = "recipe-list-item";
            recipeItem.textContent = recipe.title;

            if (String(recipe.id) === String(selectedRecipeId)) {
                recipeItem.classList.add("selected");

                recipeItem.scrollIntoView({
                    block: "nearest"
                });
            }

            recipeItem.addEventListener("click", function () {
                selectedRecipeId = recipe.id;

                document
                    .querySelectorAll(".recipe-list-item")
                    .forEach(item => {
                        item.classList.remove("selected");
                    });

                recipeItem.classList.add("selected");

                displayRecipes(recipe);
            });

            recipesContainer.appendChild(recipeItem);
        }

        return true;

    } catch (error) {
        console.error(error);
    }
}

async function restoreSession() {
    const accessToken = sessionStorage.getItem("access_token");

    if (accessToken) {
        const loaded = await loadRecipes();

        if (loaded === true) {
            loginView.hidden = true;
            appView.hidden = false;
            document.body.classList.remove("auth-checking");
            return;
        }

        sessionStorage.removeItem("access_token");
        sessionStorage.removeItem("refresh_token");
    }

    loginView.hidden = false;
    appView.hidden = true;

    document.body.classList.remove("auth-checking");
}

restoreSession();
