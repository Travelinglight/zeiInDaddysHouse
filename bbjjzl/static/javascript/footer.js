$(document).ready(function(){
    /* ----------------------- Flux count ----------------------- */
    function FluxUpdate() {
        $.get("/flux", function(data) {
            $(".flux").text(data.flux.toLocaleString());
        });
    }
    FluxUpdate();
    setInterval( function() {
        FluxUpdate();
    }, 60000);
});
