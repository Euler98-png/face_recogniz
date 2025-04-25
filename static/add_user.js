$(document).ready(function () {
    $("#addUserForm").submit(function (e) {
        e.preventDefault();
        $.ajax({
            type: "POST",
            url: addUserUrl,  // Vérifier que l'URL correspond à Django
            data: $(this).serialize(),
            dataType: "json",
            headers: { "X-Requested-With": "XMLHttpRequest" },
            success: function (response) {
                alert(response.message);
                location.reload();  // Recharger la page après succès
            },
            error: function (xhr) {
                alert("Erreur : " + xhr.responseText);
            }
        });
    });
});

$(document).ready(function(){
    $(".delete-user-form").submit(function(event){
        event.preventDefault();  // Empêcher le rechargement de la page
        
        var form = $(this);
        var url = form.attr("action");  // URL de suppression
        
        $.ajax({
            type: "POST",
            url: url,
            data: form.serialize(),  // Envoyer les données du formulaire
            dataType: "json",
            success: function(response) {
                alert(response.message);
                form.closest("tr").remove();  // Supprimer l’utilisateur du tableau
            },
            error: function(response) {
                alert("Erreur lors de la suppression.");
            }
        });
    });
});


console.log(addUserUrl);