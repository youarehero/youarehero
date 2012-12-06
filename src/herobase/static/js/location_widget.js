/**
 * Danke Niklas :-)
 */

$(function () {
    function initialize_map($addressField, $latitudeField, $longitudeField, $granularityField) {

        // FIXME: default
        // FIXME: granularity
        var latlng = new google.maps.LatLng($latitudeField.val(), $longitudeField.val());

        var $map = $('<div></div>')
            .attr("id", "map_" + $addressField.attr("id"))
            .attr("class", "map")
            .css({"width": "400px", "height": "400px"})
            .insertAfter($addressField);

        var autocomplete = new google.maps.places.Autocomplete($addressField[0]);
        $addressField.keypress(function (e) {
            if (e.which == 13) {
                return false;
            }
        });

        var mapOptions = {
            zoom: 16,
            center: latlng,
            mapTypeId: google.maps.MapTypeId.ROADMAP
        };
        var map = new google.maps.Map($map[0], mapOptions);
        var geocoder = new google.maps.Geocoder();

        var marker = new google.maps.Marker({
            position: latlng,
            map: map,
            title: "",
            draggable: true,
            animation: google.maps.Animation.DROP
        });

        var infowindow = new google.maps.InfoWindow();

        google.maps.event.addListener(autocomplete, 'place_changed', function () {
            infowindow.close();
            var place = autocomplete.getPlace();
            if (place.geometry.viewport) {
                map.fitBounds(place.geometry.viewport);
            } else {
                map.setCenter(place.geometry.location);
                map.setZoom(17);  // Why 17? Because it looks good.
            }

            marker.setPosition(place.geometry.location);
            updateCoordinates(place.geometry.location);

        });

        google.maps.event.addListener(marker, 'dragend', function (mouseEvent) {
            updateAfterDrag(marker.getPosition());
        });

        function updateCoordinates(point) {
            $latitudeField.val(point.lat());
            $longitudeField.val(point.lng());
        }

        function updateAfterDrag(point) {
            getAddress(point, 'street');
            updateCoordinates(point);
            map.panTo(point);
        }

        function getAddress(latlng, detail) {
            geocoder.geocode({'latLng': latlng}, function (results, status) {
                if (status == google.maps.GeocoderStatus.OK) {
                    var place = results[0];
                    if (place) {
                        var addressfield = document.getElementById("id_address");
                        var address;
                        if (arguments.length == 1) {
                            address = results[0].formatted_address;
                        } else if (detail == 'street') {
                            address = [
                                (place.address_components[1] && place.address_components[1].short_name || ''),
                                (place.address_components[2] && place.address_components[2].short_name || ''),
                                (place.address_components[3] && place.address_components[3].short_name || '')
                            ].join(', ');
                        } else if (detail == 'city') {
                            var city;
                            var cityRegion;
                            place.address_components.forEach(function (comp) {

                                if ($.inArray('locality', comp.types) > -1) {
                                    city = comp.short_name;
                                }

                                if ($.inArray('sublocality', comp.types) > -1) {
                                    cityRegion = comp.short_name;
                                }
                            });
                            if (city != cityRegion)
                                address = city + ", " + cityRegion;
                            else
                                address = city;
                        }
                        addressfield.value = address;
                    } else {
                        alert("No results found");
                    }
                } else {
                    alert("Geocoder failed due to: " + status);
                }
            });
        }


    }

    $('input[data-is-address-field="true"]').each(function () {
        var $addressField = $(this);
        var $latitudeField = $("#" + $addressField.data("latitudeField"));
        var $longitudeField = $("#" + $addressField.data("longitudeField"));
        var $granularityField = $("#" + $addressField.data("granularityField"));

        initialize_map($addressField, $latitudeField, $longitudeField, $granularityField);
    });
});