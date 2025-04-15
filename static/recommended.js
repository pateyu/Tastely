document.addEventListener("DOMContentLoaded", function() {
    const recipesContainer = document.querySelector('.recipes-container');

    function fetchRecommendedRecipes() {
        fetch('/api/recommended')
            .then(response => response.json())
            .then(data => {
                displayRecipes(data.recipes);
            })
            .catch(error => {
                console.error('Error loading recommended recipes:', error);
                recipesContainer.innerHTML = '<p>Error loading recipes.</p>';
            });
    }

    function displayRecipes(recipes) {
        recipesContainer.innerHTML = ''; 
        recipes.forEach(recipe => {
            const stars = renderStars(recipe.avg_rating);
            const recipeElem = document.createElement('div');
            recipeElem.className = 'bg-white rounded-lg shadow p-4 flex flex-col';
            recipeElem.innerHTML = `
                <div class="h-48 w-full overflow-hidden rounded-lg">
                    <img src="${recipe.recipe_image}" alt="${recipe.recipe_name}" class="w-full h-full object-cover">
                </div>
                <div class="flex-grow flex justify-between items-center">
                    <h3 class="font-bold text-lg mt-2">${recipe.recipe_name}</h3>
                    <div class="text-yellow-400 text-lg">${stars}</div>
                </div>
                <p class="text-gray-600">${recipe.recipe_description}</p>
                <button onclick="location.href='/recipe/${encodeURIComponent(recipe.recipe_name.replace(/ /g, '-'))}';" class="mt-3 px-4 py-2 bg-green-500 text-white rounded hover:bg-green-700 transition">View Recipe</button>
            `;
            recipesContainer.appendChild(recipeElem);
        });
    }

    function renderStars(rating) {
        let stars = '';
        for (let i = 1; i <= 5; i++) {
            if (i <= Math.round(rating)) {
                stars += '★';  // Black star
            } else {
                stars += '☆';  // White star
            }
        }
        return stars;
    }

    fetchRecommendedRecipes(); // Initial fetch of recommended recipes when the page loads
});
