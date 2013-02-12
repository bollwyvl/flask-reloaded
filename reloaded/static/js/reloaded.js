;(function(){
  "use strict";
  
  /*
    simplish way to refresh page based
  */
  
  var window = this;
  
  window.reloaded = function(options){
    options = options || {};
    
    var api = {},
      defaults = {
        interval: 1.0,
        url: "/reloaded/"
      },
      _interval = null,
      _stopped = true,
      _mtime = null;
    
    // apply defaults
    for(var opt in defaults) {
      if(!options.hasOwnProperty(opt)){
        options[opt] = defaults[opt];
      }
    }
    
    api.reload = function(mtime) {
      // force a hard reload
      if(_mtime === null){
        _mtime = mtime;
      }
      if(_mtime !== mtime){
        api.stop();
        window.location.reload(true);
      }
      
      return api;
    };

    api.fetch = function() {
      if(_stopped){return api;}
      
      var client = new XMLHttpRequest();
      
      client.onreadystatechange = function() {
        if(this.readyState == this.DONE && this.status == 200) {
          try{
            api.reload(JSON.parse(this.responseText).mtime)
          }catch(err){
            // it's probably nothing...
          }
        }
      };
      
      client.open("GET", options.url + "?r=" + Math.random());
      client.send();
      
      return api;
    };
    
    api.start = function() {
      _stopped = false;
      _interval = window.setInterval(api.fetch, options.interval * 1000);
      return api;
    };
    
    api.stop = function () {
      _stopped = true;
      window.clearInterval(_interval);
      _interval = null;
      
      return api;
    };
    
    return api;
  }
  
}).call(this);