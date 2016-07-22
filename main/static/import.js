/*
for export words from local html file to database
used to import free 5000 freq words from 
http://www.wordfrequency.info/
*/

var elem = document.createElement('script');
elem.src = "https://ajax.googleapis.com/ajax/libs/jquery/2.2.3/jquery.min.js";
document.body.appendChild(elem);


var table = $("body table:eq(3)");
var length = table.find('tr').length
var on = false;
var progress = 2;


function start() {
    on = true;
    next();
}


function stop() {
    on = false;
}


function next() {

    if (!on) {
        return false;
    }


    var tr = table.find('tr:eq('+progress+')');
    if (tr.length<1) {
        console.log("It's all done");
        return false;
    }

    var word = $.trim(tr.find('td:eq(1)').text());
    var frequency = tr.find('td:eq(3)').text();

    var postData = {
        word: word,
        frequency: frequency
    }

    $.post('https://localhost:8050/api/tmp/import', postData, function(ans){
        progress++;
        next();
    }, 'json');



}
