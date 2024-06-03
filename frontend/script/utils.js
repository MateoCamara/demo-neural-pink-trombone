function setVoiceness(voiceness) {
    const tenseness = 1 - Math.cos((voiceness) * Math.PI * 0.5);
    const loudness = Math.pow(tenseness, 0.25);

    pinkTromboneElement.tenseness.value = tenseness;
    pinkTromboneElement.loudness.value = loudness;
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function interpolateArrayValues(arr, step) {
    var interpolatedValues = [];
    for (var i = 0; i < arr.length - 1; i++) {
        var start = arr[i];
        var end = arr[i + 1];
        interpolatedValues.push(start);
        var interval = (end - start) / (step + 1);
        for (var j = 1; j <= step; j++) {
            var value = start + interval * j;
            interpolatedValues.push(value);
        }
    }
    interpolatedValues.push(arr[arr.length - 1]);
    return interpolatedValues;
}