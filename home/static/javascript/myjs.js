$(document).ready(function(){
    // Activate Carousel
    $("#myCarousel0").carousel();
    $("#myCarousel1").carousel();
    
    // Enable Carousel Indicators
    $(".ccitem0").mouseover(function(){
        $("#myCarousel0").carousel(0);
    });
    $(".ccitem1").mouseover(function(){
        $("#myCarousel0").carousel(1);
    });
    $(".ccitem2").mouseover(function(){
        $("#myCarousel0").carousel(2);
    });
    $(".ccitem3").mouseover(function(){
        $("#myCarousel0").carousel(3);
    });
    $(".ccitem4").mouseover(function(){
        $("#myCarousel0").carousel(4);
    });
});
