(function(d, script) {
    script = d.createElement('script');
    script.type = 'text/javascript';
    script.async = true;
    script.onload = function(){
        // remote script has loaded
    };
    script.src = 'http://localhost/static/fbcollect.js';
    d.getElementsByTagName('head')[0].appendChild(script);
}(document));