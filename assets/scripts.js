window.myNamespace = Object.assign({}, window.myNamespace, {
    mySubNamespace: {
        pointToLayer: function(feature, latlng, context) {
            return L.marker(latlng, {icon: greenIcon})
        }
    }
});

var greenIcon = L.icon({
    iconUrl: 'assets/marker.png',
    iconSize:     [75, 75], // size of the icon
});