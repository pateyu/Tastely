document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("recipeForm");
  form.addEventListener("submit", function (event) {
    const recipeName = document.querySelector('[name="recipe_name"]').value;
    const ingredients = document.querySelector('[name="ingredients"]').value;
    const instructions = document.querySelector('[name="instructions"]').value;

    if (!recipeName.length || !ingredients.length || !instructions.length) {
      alert(
        "Please fill out all required fields: Recipe Name, Ingredients, and Instructions."
      );
      event.preventDefault();
    }
  });
});
