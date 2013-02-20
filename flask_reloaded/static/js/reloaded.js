;(function(JSON, $){
  "use strict";

  /*
    simplish way to refresh page based
  */

  var window = this;
  
  window.reloaded = function(){

    var api = {},
      _url = "/reloaded/",
      _interval = 1.0,
      _stopped = true,
      _waiting = true,
      _mtime = null,
      _panel = false,
      _enabled = false,
      _cookie_fields = ["enabled", "interval"];

    api.init = function(){
      if(api.panel()){
        // this might do some cookie stuff
        api.init_panel();
      }else{
        api.enabled(true);
      }
      
      if(api.enabled()){
        return api.start();  
      }
      
      return api;
    };
    
    api.init_cookie = function(){
      /* if there is jquery, add cookie
       * once https://github.com/mgood/flask-debugtoolbar/pull/42 hits, this 
       * will be unnecessary
       * 
       */
      if($){
        $.cookie = function(name, value, options) { if (typeof value != 'undefined') { options = options || {}; if (value === null) { value = ''; options.expires = -1; } var expires = ''; if (options.expires && (typeof options.expires == 'number' || options.expires.toUTCString)) { var date; if (typeof options.expires == 'number') { date = new Date(); date.setTime(date.getTime() + (options.expires * 24 * 60 * 60 * 1000)); } else { date = options.expires; } expires = '; expires=' + date.toUTCString(); } var path = options.path ? '; path=' + (options.path) : ''; var domain = options.domain ? '; domain=' + (options.domain) : ''; var secure = options.secure ? '; secure' : ''; document.cookie = [name, '=', encodeURIComponent(value), expires, path, domain, secure].join(''); } else { var cookieValue = null; if (document.cookie && document.cookie != '') { var cookies = document.cookie.split(';'); for (var i = 0; i < cookies.length; i++) { var cookie = $.trim(cookies[i]); if (cookie.substring(0, name.length + 1) == (name + '=')) { cookieValue = decodeURIComponent(cookie.substring(name.length + 1)); break; } } } return cookieValue; } };
      }else{
        return;
      }
      
      var current_values = api.cookie();
            
      $.each(_cookie_fields, function(idx, to_wrap){
        var old = api[to_wrap];
        old(current_values[to_wrap]);
        api[to_wrap] = function(val){
          if(!arguments.length){return old();}
          
          api.cookie(to_wrap, val);
          return old(val);
        };
      });
    };
    
    api.cookie = function(key, val){
      var _cookie_name = "fldt-reloaded",
        current_values = {};
        
      $.each(_cookie_fields, function(idx, key){
          current_values[key] = api[key]();
      });
      
      try{
        $.extend(current_values, JSON.parse($.cookie(_cookie_name)));
      }catch(err){
        // probably just the wind
      }
      
      if(arguments.length === 0){ return current_values; }      
      if(arguments.length === 1){ return current_values[key]; }
      
      current_values[key] = val;
      
      $.cookie(_cookie_name, JSON.stringify(current_values));
      
      return api;
    };
    
    api.init_panel = function(){
      var form = $("#flDebug form.fdbt-reloaded");
      
      api.init_cookie();
      
      var chk_enbl = form.find(".fdbt-reloaded-enabled")
        .change(function(){
          api.enabled($(this).filter(":checked").length !== 0)
            .panel_subtitle()
            .restart_if_enabled();
        });
      
      if(api.enabled()){chk_enbl.attr("checked", "checked");}
      
      form.find(".fdbt-reloaded-interval")
        .val(api.interval())
        .change(function(){
          api.interval($(this).val())
            .panel_subtitle()
            .restart_if_enabled();
        });
      
      return api.panel_subtitle();
    };
    
    api.panel_subtitle = function(){
      $("#flDebugAutoreloadPanel small").text(
        api.enabled() ? ("Every " + api.interval() + " sec") : "Disabled"
      );
      return api;
    };
    
    api.panel = function(enable) {
      if(!arguments.length){return _panel;}
      
      _panel = enable;
      
      return api;
    };
    
    api.url = function(url) {
      if(!arguments.length){return _url;}
      
      _url = url;
      
      return api;
    };
    
    api.enabled = function(enable){
      if(!arguments.length){return _enabled;}
      
      _enabled = enable;
      
      return api;
    };
    
    api.interval = function(intvl){
      if(!arguments.length){return _interval}
      
      _interval = intvl;
      
      return api;
    };

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
          _waiting = false;
          try{
            api.reload(JSON.parse(this.responseText).mtime);
          }catch(err){
            // it's probably nothing...
          }
          if(!_stopped){
            window.setTimeout(api.fetch, _interval * 1000);
            _waiting = true;
          }
        }
      };

      client.open("GET", _url + "?r=" + Math.random());
      client.send();
      
      return api;
    };
    
    api.start = function() {
      _stopped = false;
      window.setTimeout(api.fetch, _interval * 1000);
      _waiting = true;
      return api;
    };
    
    api.restart_if_enabled = function() {
      api.stop();
      
      api.enabled() && api.start();
      
      return api;
    };

    api.stop = function () {
      _stopped = true;
      
      return api;
    };

    return api;
  }

}).call(this, JSON, window.jQuery && window.jQuery.noConflict(true));