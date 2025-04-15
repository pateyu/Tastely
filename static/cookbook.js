document.addEventListener("DOMContentLoaded", function() {
    const recipesContainer = document.querySelector('.recipes-container');

    function fetchCookbookRecipes() {
        fetch('/api/cookbook')
            .then(response => response.json())
            .then(data => {
                displayRecipes(data.recipes);
            })
            .catch(error => {
                console.error('Error loading cookbook recipes:', error);
                recipesContainer.innerHTML = '<p>Error loading recipes.</p>';
            });
    }

    function displayRecipes(recipes) {
        recipesContainer.innerHTML = '';
        recipes.forEach(recipe => {
            const recipeElem = document.createElement('div');
            recipeElem.className = 'bg-white rounded-lg shadow p-4 flex flex-col';
            recipeElem.innerHTML = `
                <div class="h-48 w-full overflow-hidden rounded-lg">
                    <img src="${recipe.recipe_image}" alt="${recipe.recipe_name}" class="w-full h-full object-cover">
                </div>
                <div class="flex-grow">
                    <h3 class="font-bold text-lg mt-2">${recipe.recipe_name}</h3>
                    <p class="text-gray-600">${recipe.recipe_description}</p>
                </div>
                <button onclick="location.href='/recipe/${encodeURIComponent(recipe.recipe_name.replace(/ /g, '-'))}';" class="mt-3 px-4 py-2 bg-green-500 text-white rounded hover:bg-green-700 transition">View Recipe</button>
            `;
            recipesContainer.appendChild(recipeElem);
        });
    }

    fetchCookbookRecipes(); // Initial fetch of cookbook recipes when the page loads
});
