/* Trimoco quote + chat form handler (no backend needed).
   Sends to FormSubmit (free). The FIRST real submission triggers a one-time
   activation email to info@trimoco.com - click "Activate" in it once.
   If the send fails, the visitor's email app opens with the details filled in. */
(function () {
  var TO = "info@trimoco.com";
  var ENDPOINT = "https://formsubmit.co/ajax/" + TO; // TODO(owner): swap for Web3Forms/Formspree key if preferred
  function mailto(a, source) {
    var body = "Name: " + (a.name || "") + "\nPhone: " + (a.phone || "") + "\n\n" + (a.message || "") + "\n\n(" + source + ", " + location.href + ")";
    location.href = "mailto:" + TO + "?subject=" + encodeURIComponent("Quote request - trimoco.com") + "&body=" + encodeURIComponent(body);
  }
  window.trimocoSubmit = async function (answers, source) {
    var a = answers || {};
    try {
      var r = await fetch(ENDPOINT, {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify({
          _subject: "New " + source + " lead - trimoco.com",
          _template: "table",
          _captcha: "false",
          name: a.name || "", phone: a.phone || "", message: a.message || "",
          consent: a.consent || "", page: location.href, source: source
        })
      });
      var d = await r.json().catch(function () { return {}; });
      if (r.ok && String(d.success) !== "false") {
        if (window.gtag) gtag("event", "generate_lead", { source: source });
        return true;
      }
    } catch (e) {}
    mailto(a, source);
    return false;
  };
})();
