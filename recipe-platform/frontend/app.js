const generateForm = document.getElementById("generate-form");
const requestInput = document.getElementById("request");
const validationMessage = document.getElementById("validation-message");
const generateButton = document.getElementById("generate-button");
const newRecipeButton = document.getElementById("new-recipe-button");

let selectedRecipeId = null;

const INACTIVITY_TIMEOUT =
    Number(window.APP_CONFIG.inactivityTimeoutMinutes) * 60 * 1000;
const INACTIVITY_WARNING =
    Number(window.APP_CONFIG.inactivityWarningMinutes) * 60 * 1000;

let inactivityTimer = null;
let inactivityWarningTimer = null;
let lastActivityAt = null;
let lastActivityRecordedAt = 0;
const ACTIVITY_THROTTLE = 5000;

function recordActivity() {
    lastActivityAt = Date.now();
}

function resetInactivityTimer() {
    clearTimeout(inactivityTimer);
    clearTimeout(inactivityWarningTimer);

    inactivityWarningTimer = setTimeout(
        showInactivityWarning,
        INACTIVITY_TIMEOUT - INACTIVITY_WARNING
    );

    inactivityTimer = setTimeout(
        handleInactivityTimeout,
        INACTIVITY_TIMEOUT
    );
}

["click", "keydown", "touchstart", "scroll", "mousemove"].forEach(function (eventType) {
    document.addEventListener(eventType, function () {
        if (!appView.hidden && inactivityPopup.hidden) {
            const now = Date.now();

            if (
                eventType === "scroll" ||
                eventType === "mousemove"
            ) {
                if (now - lastActivityRecordedAt < ACTIVITY_THROTTLE) {
                    return;
                }
            }

            lastActivityRecordedAt = now;
            recordActivity();
            resetInactivityTimer();
        }
    });
});

function showInactivityWarning() {
    const warningMessage =
        document.getElementById("inactivity-warning-message");

    warningMessage.textContent =
        `Your session will expire in ${window.APP_CONFIG.inactivityWarningMinutes} minutes due to inactivity!`;

    inactivityPopup.hidden = false;
}

function saveAppState() {
    const state = {
        selectedRecipeId,
        request: requestInput.value,
    };

    sessionStorage.setItem(
        "recipe_restore_state",
        JSON.stringify(state)
    );
}

async function handleInactivityTimeout() {
    inactivityPopup.hidden = true;

    saveAppState();

    await revokeRefreshSession();

    clearSession();

}

const errorPopup = document.getElementById("error-popup");
const errorPopupMessage = document.getElementById("error-popup-message");
const errorPopupOk = document.getElementById("error-popup-ok");

const inactivityPopup = document.getElementById("inactivity-popup");
const inactivityContinue = document.getElementById("inactivity-continue");
const inactivityLogout = document.getElementById("inactivity-logout");

inactivityContinue.addEventListener("click", function () {
    inactivityPopup.hidden = true;
    resetInactivityTimer();
});

inactivityLogout.addEventListener("click", function () {
    inactivityPopup.hidden = true;
    logout();
});

errorPopupOk.addEventListener("click", function() {
    errorPopup.hidden = true;
});

function startNewRecipe() {
    selectedRecipeId = null;

    generateForm.reset();

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
    updateRequestInput();

}

newRecipeButton.addEventListener("click", function () {
    startNewRecipe();
});

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
const logoutButton = document.getElementById("logout-button");


function clearSession() {
    sessionStorage.removeItem("access_token");
    sessionStorage.removeItem("refresh_token");

    clearTimeout(inactivityTimer);
    clearTimeout(inactivityWarningTimer);

    inactivityPopup.hidden = true;

    loginEmail.value = "";
    loginPassword.value = "";

    loginView.hidden = false;
    appView.hidden = true;
}

function handleSessionExpired() {
    clearSavedAppState();
    clearSession();
}

function clearSavedAppState() {
    sessionStorage.removeItem("recipe_restore_state");
}

function getSavedAppState() {
    const savedState = sessionStorage.getItem("recipe_restore_state");

    if (!savedState) {
        return null;
    }

    try {
        return JSON.parse(savedState);
    } catch (error) {
        console.error("Saved application state is invalid:", error);
        clearSavedAppState();
        return null;
    }
}

function restoreAppState(savedState) {
    requestInput.value = savedState.request || "";

    updateGenerateButton();
    updateRequestInput();

    clearSavedAppState();
}

async function revokeRefreshSession() {
    const refreshToken = sessionStorage.getItem("refresh_token");

    if (!refreshToken) {
        return;
    }

    try {
        await fetch(
            "/users/logout",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    refresh_token: refreshToken,
                }),
            }
        );
    } catch (error) {
        console.error("Session revocation request failed:", error);
    }
}

async function logout() {
    await revokeRefreshSession();

    clearSavedAppState();
    clearSession();
}

async function authenticatedFetch(url, options={}) {
    const accessToken = sessionStorage.getItem("access_token");

    if (!accessToken) {
        throw new Error("No access token");
    }

    const headers = {
        ...(options.headers || {}),
        "Authorization": `Bearer ${accessToken}`,
    };

    let response = await fetch(
        url,
        {
            ...options,
            headers: headers,
        }
    );

    if (response.status !== 401) {
        return response;
    }

    const refreshed = await refreshAccessToken();

    if (!refreshed) {
        return response;
    }

    const newAccessToken = sessionStorage.getItem("access_token");

    const retryHeaders = {
        ...(options.headers || {}),
        "Authorization": `Bearer ${newAccessToken}`,
    };

    response = await fetch(
        url,
        {
            ...options,
            headers: retryHeaders,
        }
    );

    return response;
}

async function refreshAccessToken() {
    const refreshToken = sessionStorage.getItem("refresh_token");

    if (!refreshToken) {
        return false;
    }

    const response = await fetch(
        "/users/refresh",
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                refresh_token: refreshToken,
            }),
        }
    );

    if (!response.ok) {
        return false;
    }

    const data = await response.json();

    sessionStorage.setItem(
        "access_token",
        data.access_token,
    );

    return true;
}

logoutButton.addEventListener("click", logout);

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
            data.refresh_token,
        );

        const savedState = getSavedAppState();

        if (savedState) {
            selectedRecipeId = savedState.selectedRecipeId;
        }

        loginView.hidden = true;
        appView.hidden = false;

        resetInactivityTimer();

        await loadRecipes();

        if (savedState) {
            restoreAppState(savedState);
        }

    } catch (error) {
        console.error(error);

        loginMessage.textContent =
            "Could not connect to the server.";

        loginMessage.style.color = "red";
    }
});

/*
 * Basic recipe request validation
 */

generateForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    validationMessage.textContent = "";
    validationMessage.style.color = "";

    const request = requestInput.value.trim();

    const isRefinement = selectedRecipeId !== null;

    const endpoint = isRefinement
        ? `/recipes/${selectedRecipeId}/refine`
        : "/recipes/generate";

    const actionText = isRefinement
        ? "Refining Recipe..."
        : "Generating Recipe...";

    if (!request) {
        showErrorPopup(
            "Please enter a recipe request."
        );

        requestInput.focus();

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
        actionText;

    validationMessage.style.color = "green";

    try {
        const response = await authenticatedFetch(
            endpoint,
            {
                method: "POST",
                headers: {
                    "Authorization": `Bearer ${accessToken}`,
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    request: request,
                }),
            }
        );

        if (!response.ok) {
            let message = isRefinement
                ? "Could not refine the recipe."
                : "Could not generate the recipe.";

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

            return;
        }

        const recipe = await response.json();

        console.log("Generated recipe:", recipe);

        selectedRecipeId = recipe.id;
        saveAppState();

        displayRecipes(recipe);

        try {
            await loadRecipes();
        } catch (error) {
            console.error("Loading My Recipes failed", error);
        }

        requestInput.value = "";

        validationMessage.textContent =
            isRefinement
                ? "Recipe refined successfully."
                : "Recipe generated successfully.";

        validationMessage.style.color = "green";

    } catch (error) {
        console.error(
            isRefinement
                ? "Recipe refinement failed:"
                : "Recipe generation failed:",
            error
        );

        validationMessage.textContent =
            isRefinement
                ? "Could not connect to the server while refining the recipe."
                : "Could not connect to the server while generating the recipe.";

        validationMessage.style.color = "red";

    } finally {
        updateGenerateButton();
    }

});

function updateGenerateButton() {
    if (selectedRecipeId === null) {
        generateButton.textContent = "Generate";
        generateButton.disabled = !requestInput.value.trim();
        return;
    }

    generateButton.textContent = "Refine";
    generateButton.disabled = !requestInput.value.trim();
}

function updateRequestInput() {
    if (selectedRecipeId === null) {
        requestInput.placeholder = "What would you like to cook?";
        return;
    }

    requestInput.placeholder = "Would you like to refine the recipe? Example: servings, diet?";
}

requestInput.addEventListener("input", function () {
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
        const response = await authenticatedFetch(
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
            const response = await authenticatedFetch(
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
            deletePopup.dataset.recipeTitle = recipe.title;
            deletePopup.hidden = false;
            deletePopupCancel.focus();
    });

    updateGenerateButton();
    updateRequestInput();

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
            const response = await authenticatedFetch(
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

            recipeView.innerHTML = `
                <div class="empty-state">
                    <h2>No recipe selected</h2>
                    <p>Generate a recipe or select one from My Recipes.</p>
                </div>
            `;

            updateGenerateButton();

            await loadRecipes();

            validationMessage.textContent =
                `Recipe "${document.getElementById("delete-popup").dataset.recipeTitle}" deleted successfully`
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
        const response = await authenticatedFetch(
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
                handleSessionExpired();
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

                displayRecipes(recipe);
            }

            recipeItem.addEventListener("click", function () {
                selectedRecipeId = recipe.id;
                saveAppState();
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
        const savedState = getSavedAppState();

        if (savedState) {
            selectedRecipeId = savedState.selectedRecipeId;
        }

        const loaded = await loadRecipes();

        if (loaded === true) {
            loginView.hidden = true;
            appView.hidden = false;

            resetInactivityTimer();

            if (savedState) {
                restoreAppState(savedState);
            }

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
