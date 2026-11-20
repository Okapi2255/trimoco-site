/* Design-page estimate form. Posts to FormSubmit for the design lead inbox.
   Matches the site's existing FormSubmit field set. Does not use the sitewide
   Trimoco forms.js endpoint. The recipient address is not shown on the page. */
(function () {
  var TO = "rogerinny@gmail.com";
  var ENDPOINT = "https://formsubmit.co/ajax/" + TO;

  var phoneRe = /(?:ext(?:ension)?\.?|x|#)\s*(\d*)\s*$/i;

  function digitsNational(value) {
    var t = (value || "").trim();
    if (!t) return { national: "", extension: "" };
    var m = t.match(phoneRe);
    var rest = t;
    var ext = "";
    if (m && m.index !== undefined && m.index > 0) {
      ext = m[1] || "";
      rest = t.slice(0, m.index);
    }
    var s = rest.replace(/\D/g, "");
    if (s.startsWith("001") && s.length > 3) s = s.slice(3);
    if ((t.indexOf("+") >= 0 && s.startsWith("1") && s.length > 1) || (s.length >= 11 && s.startsWith("1"))) {
      s = s.slice(1);
    }
    if (!m && s.length > 10) {
      ext = s.slice(10);
      s = s.slice(0, 10);
    }
    return { national: s, extension: ext };
  }

  function validNational(d) {
    if (d.length !== 10) return false;
    return d[0] >= "2" && d[0] <= "9" && d[3] >= "2" && d[3] <= "9";
  }

  function formatNational(d) {
    if (!d.length) return "";
    if (d.length < 3) return d;
    var a = d.slice(0, 3), b = d.slice(3, 6), c = d.slice(6, 10);
    if (d.length === 3) return "(" + a;
    if (d.length <= 6) return "(" + a + ") " + b;
    return "(" + a + ") " + b + "-" + c;
  }

  function formatPhone(value) {
    var p = digitsNational(value);
    var n = formatNational(p.national);
    return p.extension ? (n ? n + " ext. " + p.extension : "ext. " + p.extension) : n;
  }

  function e164(value) {
    var p = digitsNational(value);
    return validNational(p.national) ? "+1" + p.national : null;
  }

  function phoneError(code) {
    if (code === "short") return "Enter a 10-digit US or Canada number, including the area code.";
    if (code === "long") return "That number has too many digits.";
    if (code === "invalid") return "Check the number. US and Canada numbers can't start with 0 or 1.";
    return "";
  }

  function validatePhone(input) {
    var t = input.value.trim();
    if (!t) {
      input.setCustomValidity("");
      return !input.required;
    }
    var p = digitsNational(t);
    if (p.national.length < 10) {
      input.setCustomValidity(phoneError("short"));
      return false;
    }
    if (p.national.length > 10 || (p.extension && p.extension.length > 6)) {
      input.setCustomValidity(phoneError("long"));
      return false;
    }
    if (!validNational(p.national)) {
      input.setCustomValidity(phoneError("invalid"));
      return false;
    }
    input.setCustomValidity("");
    return true;
  }

  function bindPhone(input) {
    input.addEventListener("input", function () {
      var caretDigits = (input.value.slice(0, input.selectionStart || input.value.length).match(/\d/g) || []).length;
      var formatted = formatPhone(input.value);
      if (formatted !== input.value) {
        input.value = formatted;
        var n = 0, pos = formatted.length, i;
        for (i = 0; i < formatted.length; i++) {
          if (formatted[i] >= "0" && formatted[i] <= "9") {
            n++;
            if (n === caretDigits) { pos = i + 1; break; }
          }
        }
        input.setSelectionRange(pos, pos);
      }
      var p = digitsNational(input.value);
      if (!input.value.trim() || validNational(p.national)) input.setCustomValidity("");
    });
    input.addEventListener("blur", function () {
      if (input.value.trim()) validatePhone(input);
    });
  }

  document.querySelectorAll("[data-design-lead-form]").forEach(function (wrap) {
    var form = wrap.querySelector("[data-lead-form]");
    var heading = wrap.querySelector("[data-lead-form-heading]");
    var success = wrap.querySelector("[data-lead-form-success]");
    var fail = wrap.querySelector("[data-lead-form-error]");
    var consent = form && form.querySelector('input[name="consent"]');
    var submit = form && form.querySelector('button[type="submit"]');
    if (!form) return;

    var phones = form.querySelectorAll("[data-phone-input]");
    phones.forEach(bindPhone);

    function syncConsent() {
      if (!consent) return;
      consent.setCustomValidity(consent.checked ? "" : (consent.getAttribute("data-consent-error") || "Please agree to continue."));
    }
    syncConsent();
    if (consent) consent.addEventListener("change", syncConsent);

    form.addEventListener("submit", async function (e) {
      e.preventDefault();
      syncConsent();
      phones.forEach(validatePhone);
      if (!form.checkValidity()) {
        form.reportValidity();
        return;
      }
      var data = new FormData(form);
      if (String(data.get("bot-trap") || "").trim()) return;
      var payload = {
        _subject: "New design page lead - trimoco.com",
        _template: "table",
        _captcha: "false",
        name: String(data.get("name") || ""),
        phone: e164(String(data.get("phone") || "")) || String(data.get("phone") || ""),
        message: String(data.get("message") || ""),
        consent: String(data.get("consent") || ""),
        page: location.href,
        source: "Design page form"
      };
      var label = submit && submit.getAttribute("data-submit-label");
      var original = submit ? submit.textContent : "";
      if (submit) {
        submit.disabled = true;
        if (label) submit.textContent = label;
      }
      var ok = false;
      try {
        var r = await fetch(ENDPOINT, {
          method: "POST",
          headers: { "Content-Type": "application/json", Accept: "application/json" },
          body: JSON.stringify(payload)
        });
        var d = await r.json().catch(function () { return {}; });
        ok = r.ok && String(d.success) !== "false";
        if (ok && window.gtag) gtag("event", "generate_lead", { source: "Design page form" });
      } catch (err) {
        ok = false;
      }
      if (ok) {
        form.hidden = true;
        if (heading) heading.hidden = true;
        if (fail) fail.hidden = true;
        if (success) success.hidden = false;
      } else {
        if (fail) fail.hidden = false;
        if (submit) {
          submit.disabled = false;
          submit.textContent = original;
        }
      }
    });
  });
})();
