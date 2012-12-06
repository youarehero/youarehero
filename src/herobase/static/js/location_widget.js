/**
 * Created with PyCharm.
 * User: raphael
 * Date: 06.12.12
 * Time: 12:12
 * To change this template use File | Settings | File Templates.
 */

$(function () {
    $('input[data-location-field="true"]').each(function () {
        var $locationField = $(this);
        var $latitudeField = $("#" + $locationField.data("latitudeField"));
        var $longitudeField = $("#" + $locationField.data("longitudeField"));
        var $granularityField = $("#" + $locationField.data("granularityField"));



        $locationField.css({"width": "390px"});
        var $map = $("<div></div>")
            .attr("id", "map_" + $locationField.attr("id"))
            .insertAfter($locationField)
            .css({'width': '400px', 'height': '400px'});

        var latlng = new google.maps.LatLng(51,10);

        var mapOptions = {
            zoom: 5,
            center: latlng,
            mapTypeId: 'roadmap'
        };
        var map = new google.maps.Map($map[0], mapOptions);
        var geocoder = new google.maps.Geocoder();
        var marker = new google.maps.Marker({map: map});

        var codeAddress = function() {
            geocoder.geocode({ 'address': $locationField.val()}, function (results, status) {
                console.debug(results, status);
                if (status == google.maps.GeocoderStatus.OK) {
                    var result = results[0];

                    var zoomLevel = 14;
                    if ($.contains(result.types, "locality") && $.contains(result.types, "political")) {
                        var zoomLevel = 12;
                    }

                    map.setCenter(results [0].geometry.location);
                    map.setZoom(zoomLevel);
                    marker.setPosition(results [0].geometry.location);
                }
                else {
                }
            });
        };
        $locationField.blur(codeAddress);
    });
});