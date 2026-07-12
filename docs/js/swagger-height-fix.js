// Fallback height sync for swagger-ui-tag iframes.
// The plugin's child page calls parent.update_swagger_ui_iframe_height() from a
// ResizeObserver, but the parent defines that function inside document$.subscribe,
// which can run AFTER the iframe finished rendering - the calls are lost and the
// iframe stays at the browser-default ~150px. This polls for a while after load
// and syncs any swagger iframe to its content height, then stops.
(function () {
  function sync() {
    document.querySelectorAll("iframe.swagger-ui-iframe").forEach(function (f) {
      try {
        var h = f.contentWindow.document.body.scrollHeight;
        if (h > 100 && Math.abs(f.offsetHeight - (h + 80)) > 8) {
          f.style.height = (h + 80) + "px";
          f.height = h + 80;
        }
      } catch (e) { /* cross-origin or not ready yet */ }
    });
  }
  var timer = setInterval(sync, 600);
  setTimeout(function () { clearInterval(timer); }, 20000);
  window.addEventListener("load", sync);
})();
