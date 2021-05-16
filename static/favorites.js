$('.favorite').on('click', '.favorite-btn', removeFavorite);
$('.favorite').on('click', '.non-favorite-btn', addFavorite);

async function addFavorite(){
    let dishId = $(this).data('id');
    response = await axios.post(`/favorites/${dishId}`);

    $(this).removeClass('non-favorite-btn');
    $(this).html('Remove from Favorites');
    $(this).addClass('favorite-btn');
}

async function removeFavorite() {
    let dishId = $(this).data('id');
    response = await axios.post(`/removefavorite/${dishId}`)

    $(this).removeClass("favorite-btn");
    $(this).html('Add to Favorites');
    $(this).addClass("non-favorite-btn");
}