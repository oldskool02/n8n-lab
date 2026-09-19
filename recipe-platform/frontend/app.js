const servingsSelect = document.getElementById("servings");
const dietSelect = document.getElementById("diet");
const cuisineSelect = document.getElementById("cuisine");
const generateForm = document.getElementById("generate-form");
const requestInput = document.getElementById("request");
const validationMessage = document.getElementById("validation-message");
const generateButton = document.getElementById("generate-button");

let selectedRecipeId = null;
let savedCriteria = {
    servings: 2,
    diet: "",
    cuisine: "",
}

const errorPopup = document.getElementById("error-popup");
const errorPopupMessage = document.getElementById("error-popup-message");
const errorPopupOk = document.getElementById("error-popup-ok");


errorPopupOk.addEventListener("click", function() {
    errorPopup.hidden = true;
});

function criteriaChanged() {
    return (
        Number(servingsSelect.value) !== savedCriteria.servings ||
        dietSelect.value !== savedCriteria.diet ||
        cuisineSelect.value !== savedCriteria.cuisine
    );
}

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

    updateGenerateButton();

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
            "/users/login",
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

    const isRegeneration =
        selectedRecipeId !== null && criteriaChanged();

    validationMessage.textContent = "";
    validationMessage.style.color = "";

    const request = requestInput.value.trim();
    const servings = Number(servingsSelect.value);

    if (!isRegeneration && request.length < 6) {
        showErrorPopup(
            "Please enter a recipe request that is at least 6 characters"
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

    validationMessage.textContent =
        isRegeneration
            ? "Regenerating recipe..."
            : "Generating recipe...";

    validationMessage.style.color = "green";

    try {
        const response = await fetch(
            isRegeneration
                ? `/recipes/${selectedRecipeId}`
                : "/recipes/generate",
            {
                method: isRegeneration ?"PUT" : "POST",
                headers: {
                    "Authorization": `Bearer ${accessToken}`,
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(
                    isRegeneration
                        ? {
                            servings: servings,
                            diet: dietSelect.value || null,
                            cuisine: cuisineSelect.value || null,
                        }
                        : {
                            request: request,
                            servings: servings,
                            diet: dietSelect.value || null,
                            cuisine: cuisineSelect.value || null,
                        }
                ),
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
            if (!isRegeneration) {
                generateForm.reset();

                servingsSelect.value = 2;
                dietSelect.value = "";
                cuisineSelect.value = "";
            }
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

        requestInput.value = "";

        validationMessage.textContent =
            isRegeneration
                ? "Recipe regenerated successfully."
                : "Recipe generated successfully."

        validationMessage.style.color = "green";

    } catch (error) {
        console.error("Recipe generation failed:", error);

        validationMessage.textContent = "Could not connect to the server.";
        validationMessage.style.color = "red";
    } finally {
        updateGenerateButton();
    }

});

generateButton.addEventListener("click", function(event) {
    if (selectedRecipeId !== null && !criteriaChanged()) {
        event.preventDefault();
        startNewGeneration();
    }
});

function updateGenerateButton() {
    if (selectedRecipeId === null) {
        generateButton.textContent = "Generate";
        generateButton.disabled = requestInput.value.trim().length < 6;
        return;
    }

    if (criteriaChanged()) {
        generateButton.textContent = "Regenerate";
        generateButton.disabled = false;
    } else {
        generateButton.textContent = "New Generation";
        generateButton.disabled = false;
    }
}

servingsSelect.addEventListener("change", updateGenerateButton);
dietSelect.addEventListener("change", updateGenerateButton);
cuisineSelect.addEventListener("change", updateGenerateButton);

requestInput.addEventListener("input", function () {
    const request = requestInput.value.trim();

    if (selectedRecipeId !== null && request) {
        startNewGeneration();
        requestInput.value = request;
    }

    updateGenerateButton();
});

async function loadRecipeImage(recipeImage, recipe) {
    if (!recipe.image_file_id) {
        return;
    }

    const accessToken = sessionStorage.getItem("access_token");

    if (!accessToken) {
        return;
    }

    try {
        const response = await fetch(
            `/recipes/${recipe.id}/image`,
            {
                method: "GET",
                headers: {
                    "Authorization": `Bearer ${accessToken}`
                },
            }
        );

        if (!response.ok) {
            recipeImage.src = "images/recipe-fallback.png";
            recipeImage.style.visibility = "visible";
            return;
        }

        const imageBlob = await response.blob();
        recipeImage.src = URL.createObjectURL(imageBlob);
        recipeImage.style.visibility = "visible";

    } catch (error) {
        console.error("Could not load recipe image", error);
        recipeImage.src = "images/recipe-fallback.png";
        recipeImage.style.visibility = "visible";
    }
}

function displayRecipes(recipe) {
    const recipeView = document.getElementById("recipe-view");

    selectedRecipeId = recipe.id;

    savedCriteria = {
        servings: recipe.servings,
        diet: recipe.diet || "",
        cuisine: recipe.cuisine || "",
    }

    servingsSelect.value = String(recipe.servings);
    dietSelect.value = recipe.diet || "";
    cuisineSelect.value = recipe.cuisine || "";

    generateButton.textContent = "New Generation";

    recipeView.innerHTML = "";

    const recipeCard = document.createElement("div");
    recipeCard.className = "recipe-card";
    recipeView.appendChild(recipeCard);

    const recipeImageColumn = document.createElement("div");
    recipeImageColumn.className = "recipe-card-image";
    recipeCard.appendChild(recipeImageColumn);

    const recipeDetails = document.createElement("div");
    recipeDetails.className = "recipe-details";
    recipeCard.appendChild(recipeDetails);


    const title = document.createElement("h2");
    title.textContent = recipe.title;
    recipeDetails.appendChild(title);

    const recipeImage = document.createElement("img");

    if (recipe.image_file_id) {
        recipeImage.style.visibility = "hidden";
    } else {
        recipeImage.src = "images/recipe-fallback.png";
    }

    recipeImage.alt = recipe.title;
    recipeImage.className = "recipe-image";
    recipeImageColumn.appendChild(recipeImage);

    loadRecipeImage(recipeImage, recipe);

    const servings = document.createElement("p");
    servings.textContent = `Servings: ${recipe.servings}`;
    recipeDetails.appendChild(servings);

    const ingredientsHeading = document.createElement("h3");
    ingredientsHeading.textContent = "Ingredients";
    recipeDetails.appendChild(ingredientsHeading);

    const ingredientsList = document.createElement("ul");

    for (const item of recipe.ingredients) {
        const ingredientItem = document.createElement("li");

        const quantity = item.quantity || "";
        const unit = item.unit || "";
        const ingredient = item.ingredient || "";

        ingredientItem.textContent = `${quantity} ${unit} ${ingredient}`.trim();

        ingredientsList.appendChild(ingredientItem);
    }

    recipeDetails.appendChild(ingredientsList);

    const stepHeading = document.createElement("h3");
    stepHeading.textContent = "Method";
    recipeDetails.appendChild(stepHeading);

    const stepsList = document.createElement("ol");

    for (const step of recipe.steps) {
        const stepItem = document.createElement("li");

        stepItem.textContent = step.instruction;

        stepsList.appendChild(stepItem);
    }

    recipeDetails.appendChild(stepsList);

    const recipeActions = document.createElement("div");

    recipeActions.id = "recipe-actions";

    recipeDetails.appendChild(recipeActions);

    const pdfButton = document.createElement("button");
    pdfButton.type = "button";
    pdfButton.id = "download-pdf-button";
    pdfButton.textContent = "Download PDF";

    recipeActions.appendChild(pdfButton);

    pdfButton.addEventListener("click", async function() {
        const accessToken = sessionStorage.getItem("access_token");

        if (!accessToken) {
            return;
        }

        try {
            const response = await fetch(
                `/recipes/${recipe.id}/pdf`,
                {
                    method: "GET",
                    headers: {
                        "Authorization": `Bearer ${accessToken}`,
                    },
                }
            );

            if (!response.ok) {
                throw new Error("Failed to download PDF");
            }

            const blob = await response.blob();
            const url = URL.createObjectURL(blob);

            const link = document.createElement("a");
            link.href = url;
            link.download = `${recipe.title}.pdf`;
            document.body.appendChild(link);
            link.click();
            link.remove();

            URL.revokeObjectURL(url);
        } catch (error) {
            console.error("PDF download failed:", error);
        }
    });

    const deleteButton = document.createElement("button");
    deleteButton.type = "button";
    deleteButton.id = "delete-recipe-button";
    deleteButton.textContent = "Delete Recipe";

    recipeActions.appendChild(deleteButton);

    deleteButton.addEventListener("click", function () {
        const deletePopup = document.getElementById("delete-popup");
        const deletePopupMessage =
            document.getElementById("delete-popup-message");
        const deletePopupCancel =
            document.getElementById("delete-popup-cancel");

            deletePopupMessage.innerHTML = `
                <span>Are you sure you want to delete:</span>
                <span>"${recipe.title}"?</span>
                <strong>This action cannot be undone.</strong>
            `;
            deletePopup.hidden = false;
            deletePopupCancel.focus();
    });

}

document
    .getElementById("delete-popup-cancel")
    .addEventListener("click", function () {
        document.getElementById("delete-popup").hidden = true;
    });

document
    .getElementById("delete-popup")
    .addEventListener("keydown", function (event) {
            if (event.key === "Enter") {
                event.preventDefault();

                document.getElementById("delete-popup").hidden = true
           }
    });

document
    .getElementById("delete-popup-confirm")
    .addEventListener("click", async function () {
        const recipeView = document.getElementById("recipe-view");

        const accessToken = sessionStorage.getItem("access_token");

        if (!accessToken || selectedRecipeId === null) {
            return;
        }

        try {
            const response = await fetch(
                `/recipes/${selectedRecipeId}`,
                {
                    method: "DELETE",
                    headers: {
                        "Authorization": `Bearer ${accessToken}`,
                    },
                }
            );

            if (!response.ok) {
                throw new Error("Could not delete recipe");
            }

            document.getElementById("delete-popup").hidden = true;

            selectedRecipeId = null;

            generateForm.reset();

            servingsSelect.value = 2;

            dietSelect.value = "";
            cuisineSelect.value = "";

            savedCriteria = {
                servings: 2,
                diet: "",
                cuisine: "",
            };

            recipeView.innerHTML = `
                <div class="empty-state">
                    <h2>No recipe selected</h2>
                    <p>Generate a recipe or select one from My Recipes.</p>
                </div>
            `;

            updateGenerateButton();

            await loadRecipes();

            validationMessage.textContent =
                "Recipe deleted successfully.";
            validationMessage.style.color = "green"

    } catch (error) {
        console.error("Recipe deletion failed:", error);

        document.getElementById("delete-popup").hidden = true;

        validationMessage.textContent =
            "Could not delete the recipe.";
        validationMessage.style.color = "red"
    }
});

async function loadRecipes() {
    const accessToken = sessionStorage.getItem("access_token");

    if (!accessToken) {
        return;
    }

    try {
        const response = await fetch(
            "/recipes/",
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
                requestInput.value = "";

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
