$('.favorite').on('click', '.favorite-btn', removeFavorite);
$('.favorite').on('click', '.non-favorite-btn', addFavorite);

async function addFavorite(){
    let dishId = $(this).data('id');
    response = await axios.post(`/favorites/${dishId}`);

    $(this).removeClass('non-favorite-btn');
    $(this).html('<i class="fas fa-star"></i> Remove from Favorites');
    $(this).addClass('favorite-btn');
}

async function removeFavorite() {
    let dishId = $(this).data('id');
    response = await axios.get(`/removefavorite/${dishId}`)

    $(this).removeClass("favorite-btn");
    $(this).html('<i class="fas fa-star"></i> Add to Favorites');
    $(this).addClass("non-favorite-btn");
}