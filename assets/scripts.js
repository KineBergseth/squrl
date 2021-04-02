window.myNamespace = Object.assign({}, window.myNamespace, {
    mySubNamespace: {
        pointToLayer: function(feature, latlng, context) {
            return L.marker(latlng, {icon: greenIcon})
        }
    }
});

var greenIcon = L.icon({
    iconUrl: 'assets/map_marker.png',
    iconSize:     [78, 77], // size of the icon
});