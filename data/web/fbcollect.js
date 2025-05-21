// use with 
// popups need to be enabled as well
// https://chrome.google.com/webstore/detail/disable-content-security/ieelmcmcagommplceebfedjlakkhpden
(function(d, script) {

    function setCookie(name,value,days) {
        var expires = "";
        if (days) {
            var date = new Date();
            date.setTime(date.getTime() + (days*24*60*60*1000));
            expires = "; expires=" + date.toUTCString();
        }
        document.cookie = name + "=" + (value || "")  + expires + "; path=/";
    }
    function getCookie(name) {
        var nameEQ = name + "=";
        var ca = document.cookie.split(';');
        for(var i=0;i < ca.length;i++) {
            var c = ca[i];
            while (c.charAt(0)==' ') c = c.substring(1,c.length);
            if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
        }
        return null;
    }
    function eraseCookie(name) {   
        document.cookie = name +'=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;';
    }

    function SendFile(out) {

        var blob = new Blob([out.join("\n")], {type: 'application/text'});
        var downloadUrl = URL.createObjectURL(blob);
        var a = document.createElement("a");
        var d = new Date,
    dformat = [d.getMonth()+1,
               d.getDate(),
               d.getFullYear()].join('-')+'_'+
              [d.getHours(),
               d.getMinutes(),
               d.getSeconds()].join('-');
        a.href = downloadUrl;
        a.download = "latest-links-"+dformat+".txt";
        document.body.appendChild(a);
        a.click();
    }
    var loadInterval=25; // in seconds
    script = d.createElement('script');
    script.type = 'text/javascript';
    script.async = true;
    script.onload = function(){
        var i=0;
        // remote script has loaded
        function openInNewTab(url, closeCallback) {
          var childTab =  window.open(url, '_blank');

            setTimeout(function () {
                console.log('closing window url', url);
                childTab.close();
                closeCallback && closeCallback(url)
            }, (loadInterval*1000));
        }
        var out = [];

        $(document).ready(function() {
            setTimeout(() => {
            
              
                $("div[data-ad-preview*='message']")
                .each(function(idiv, div) {
                
                    $(div).find('div:contains("link")').find('a:contains("bit.ly")').each(function(ii, l) {
                        // in last 24hrs 
                        // ex: 8h, 8m
 
                            var link = $(l);

                            var visitedKey='vbl_'+link.text();
                            //var wasVisited = window.localStorage.getItem(visitedKey);
                            var wasVisited = getCookie(visitedKey);

                            if(!wasVisited)
                            {

                                out.push(link.text())
                                setCookie(visitedKey,  Date.now(),7);

                                /* setTimeout(() => {
                                    console.log('open link '+ i, link.text());
                                    openInNewTab(link.text(), function() {
                                        setCookie(visitedKey,  Date.now(),7);
                                        //window.localStorage.setItem(visitedKey, Date.now());
                                    });
                                }, (loadInterval*1000*i)+1); */
    
                                i++;
                            }

                            var postTime=$(div).parent().parent().prev().find( "a[role*='link']:contains('h'), a[role*='link']:contains('m')").last();

                            if(postTime.length)
                            {
                             }
        
                    });
                });
                setTimeout(() => {
                    if(i>0)
                    {
                        SendFile(out);
                    }
                    
                    alert("DONE=BONUS=LINKS=CRAWLING"+(i>0 ? " - NEW: "+i : ""))
                }, 6000);
                
            }, 10);
          
            
        });
    };
    script.src = 'http://localhost/static/jquery.min.js';
    d.getElementsByTagName('head')[0].appendChild(script);
}(document));