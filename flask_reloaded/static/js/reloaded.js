;(function($){
  "use strict";

  /*
    simplish way to refresh page based
  */

  var window = this;
  
  window.reloaded = function(){

    var api = {},
      _url = "/reloaded/",
      _interval = 1.0,
      _interval_id = null,
      _stopped = true,
      _mtime = null,
      _panel = false,
      _enabled = false;

    api.init = function(){
      if(api.panel()){
        return api.init_panel();
      }
      
      return api.start();
    };
    
    api.cookie_up = function(){
      // if there is jquery, add cookie
      if($){
        $.cookie = function(name, value, options) { if (typeof value != 'undefined') { options = options || {}; if (value === null) { value = ''; options.expires = -1; } var expires = ''; if (options.expires && (typeof options.expires == 'number' || options.expires.toUTCString)) { var date; if (typeof options.expires == 'number') { date = new Date(); date.setTime(date.getTime() + (options.expires * 24 * 60 * 60 * 1000)); } else { date = options.expires; } expires = '; expires=' + date.toUTCString(); } var path = options.path ? '; path=' + (options.path) : ''; var domain = options.domain ? '; domain=' + (options.domain) : ''; var secure = options.secure ? '; secure' : ''; document.cookie = [name, '=', encodeURIComponent(value), expires, path, domain, secure].join(''); } else { var cookieValue = null; if (document.cookie && document.cookie != '') { var cookies = document.cookie.split(';'); for (var i = 0; i < cookies.length; i++) { var cookie = $.trim(cookies[i]); if (cookie.substring(0, name.length + 1) == (name + '=')) { cookieValue = decodeURIComponent(cookie.substring(name.length + 1)); break; } } } return cookieValue; } };
      }
      
      ["enabled", "duration"].map(function(to_wrap){
        var old = api[to_wrap],
          cname = "fldt-reloaded-" + to_wrap;
          
        try{
          old(JSON.parse($.cookie(cname)).val);
        }catch(err){
          // probably just the wind
        }
        
        api[to_wrap] = function(val){
          if(!arguments.length){return old();}
          
          $.cookie(cname, JSON.stringify({val: val}));
          return old(val);
        };
      });
    };
    
    api.init_panel = function(){
      api.cookie_up();
      
      var form = $("#flDebug form.fdbt-reloaded"),
        subtitle = $("#flDebugAutoreloadPanel small"),
        update_subtitle = function(){
          subtitle.text(
            api.enabled() ? ("Every " + api.interval() + " sec") : "Disabled"
          );
        };
      
      update_subtitle();
      
      form.find(".fdbt-reloaded-enabled")
        .val(api.enabled())
        .change(function(){
          api
            .enabled($(this).filter(":checked").length !== 0)
            .restart_if_enabled();
          update_subtitle();
        });
      
      form.find(".fdbt-reloaded-interval")
        .val(api.interval())
        .change(function(){
          api.interval($(this).val())
            .restart_if_enabled();
          update_subtitle();
        });
      
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
          try{
            api.reload(JSON.parse(this.responseText).mtime)
          }catch(err){
            // it's probably nothing...
          }
        }
      };

      client.open("GET", _url + "?r=" + Math.random());
      client.send();

      return api;
    };
    
    api.start = function() {
      _stopped = false;
      _interval_id = window.setInterval(api.fetch, _interval * 1000);
      return api;
    };
    
    api.restart_if_enabled = function() {
      api.stop();
      
      api.enabled() && api.start();
      
      return api;
    };

    api.stop = function () {
      _stopped = true;
      window.clearInterval(_interval_id);
      _interval_id = null;
      
      return api;
    };

    return api;
  }

}).call(this, window.jQuery && window.jQuery.noConflict(true));