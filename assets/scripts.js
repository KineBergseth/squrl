window.myNamespace = Object.assign({}, window.myNamespace, {
    mySubNamespace: {
        pointToLayer: function(feature, latlng, context) {
            return L.marker(latlng, {icon: greenIcon})
        }
    }
});

var greenIcon = L.icon({
    iconUrl: 'https://www.freeiconspng.com/uploads/squirrel-png-20.png',
    iconSize:     [45, 80], // size of the icon
});