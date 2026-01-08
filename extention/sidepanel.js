// ================= PDF.js SETUP =================
pdfjsLib.GlobalWorkerOptions.workerSrc =
  chrome.runtime.getURL("lib/pdf/pdf.worker.js");

// ================= DOM ELEMENTS =================
const btn = document.getElementById("readText");
const output = document.getElementById("output");

// ================= AUTO SCAN ENTRY ================= 
document.addEventListener("DOMContentLoaded", () => {
  autoScan();
});

// ================= MANUAL FALLBACK =================
btn.addEventListener("click", () => {
  autoScan(true);
});

// ================= AUTO SCAN =================
async function autoScan(isManual = false) {
  try {
    output.innerHTML = `<li>${isManual ? "Re-scanning" : "Auto-scanning"} for policy links...</li>`;

    const links = await scanForPolicyLinks();

    if (!links.length) return;

    // 🔹 Priority: Privacy > Cookie > Terms > Others
    const priorityOrder = ["privacy", "cookie", "terms", "policy", "legal"];

    const selected =
      links.find(l =>
        priorityOrder.some(p => l.text.toLowerCase().includes(p))
      ) || links[0];

    output.innerHTML = `<li>Using policy: <b>${selected.text}</b></li>`;

    handlePolicyLink(selected.href);

  } catch (err) {
    output.innerHTML = `<li>Scan failed: ${err.message}</li>`;
  }
}

// ================= SCAN PAGE =================
async function scanForPolicyLinks() {
  const [tab] = await chrome.tabs.query({
    active: true,
    currentWindow: true
  });

  // 🚫 Block restricted URLs
  if (!tab?.url || !tab.url.startsWith("http")) {
    output.innerHTML = "<li>Cannot scan this page (restricted URL)</li>";
    return [];
  }

  const [{ result }] = await chrome.scripting.executeScript({
    target: { tabId: tab.id },
    func: () => {
      return [...document.querySelectorAll("a")]
        .map(a => ({
          text: a.innerText.trim(),
          href: a.href
        }))
        .filter(l =>
          l.text &&
          /privacy|cookie|terms|policy|legal/i.test(l.text)
        );
    }
  });

  return result || [];
}

// ================= CORE ROUTER =================
async function handlePolicyLink(url) {
  output.innerHTML = "<li>Collecting cookies, CMP & policy...</li>";

  const [tab] = await chrome.tabs.query({
    active: true,
    currentWindow: true
  });

  const domCookies = await getDomCookies(tab.id);
  const browserCookies = await getBrowserCookies(url);
  const cmpInfo = await getCMPInfo(tab.id);

  if (url.toLowerCase().endsWith(".pdf")) {
    fetchPDF(url, domCookies, browserCookies, cmpInfo);
  } else {
    fetchHTML(url, domCookies, browserCookies, cmpInfo);
  }
}

// ================= DOM COOKIES =================
async function getDomCookies(tabId) {
  const [{ result }] = await chrome.scripting.executeScript({
    target: { tabId },
    func: () => {
      return document.cookie
        .split("; ")
        .filter(Boolean)
        .map(c => {
          const [name, value] = c.split("=");
          return { name, value };
        });
    }
  });

  return result || [];
}

// ================= BROWSER COOKIES =================
function getBrowserCookies(url) {
  return new Promise(resolve => {
    chrome.runtime.sendMessage(
      { type: "GET_COOKIES", url },
      res => resolve(res?.cookies || [])
    );
  });
}

// ================= HTML POLICY =================
function fetchHTML(url, domCookies, browserCookies, cmpInfo) {
  chrome.runtime.sendMessage(
    { type: "FETCH_POLICY", url },
    response => {
      if (!response || response.error) {
        output.innerHTML = "<li>Error loading policy</li>";
        return;
      }

      const parser = new DOMParser();
      const doc = parser.parseFromString(response.html, "text/html");
      const text = doc.body.innerText;

      buildAndRenderJSON(url, text, domCookies, browserCookies, cmpInfo);
    }
  );
}

// ================= PDF POLICY =================
function fetchPDF(url, domCookies, browserCookies, cmpInfo) {
  chrome.runtime.sendMessage(
    { type: "FETCH_PDF", url },
    async response => {
      if (!response || response.error) {
        output.innerHTML = "<li>Error loading PDF</li>";
        return;
      }

      try {
        const uint8Array = new Uint8Array(response.bytes);
        const pdf = await pdfjsLib.getDocument({ data: uint8Array }).promise;

        let text = "";

        for (let i = 1; i <= pdf.numPages; i++) {
          const page = await pdf.getPage(i);
          const content = await page.getTextContent();
          text += content.items.map(item => item.str).join(" ") + "\n\n";
        }

        buildAndRenderJSON(url, text, domCookies, browserCookies, cmpInfo);
      } catch (err) {
        output.innerHTML = `<li>PDF parse error: ${err.message}</li>`;
      }
    }
  );
}

// ================= CMP DETECTION =================
function detectCMP() {
  return {
    detected: {
      tcf: typeof window.__tcfapi === "function",
      usp: typeof window.__uspapi === "function",
      gpp: typeof window.__gpp === "function"
    },
    providers: {
      onetrust: !!window.OneTrust,
      cookiebot: !!window.Cookiebot,
      didomi: !!window.didomi,
      quantcast: !!window.__cmp
    },
    consentCookies: document.cookie
      .split("; ")
      .filter(c => /consent|optanon|euconsent/i.test(c))
      .map(c => c.split("=")[0]),
    page: location.hostname
  };
}

async function getCMPInfo(tabId) {
  const [{ result }] = await chrome.scripting.executeScript({
    target: { tabId },
    func: detectCMP
  });

  return result;
}

// ================= BUILD JSON + RENDER =================
async function buildAndRenderJSON(url, text, domCookies, browserCookies, cmpInfo) {

  // 🔹 Policy JSON (for summarizer)
  const policyJSON = {
    url: url,
    raw_text: text,
    captured_at: new Date().toISOString()
  };

  // 🔹 Cookies JSON (for analyzer)
  const cookiesJSON = {
    url: url,
    cmp: cmpInfo,
    cookies: {
      dom: domCookies,
      browser: browserCookies.map(c => ({
        name: c.name,
        domain: c.domain,
        secure: c.secure,
        httpOnly: c.httpOnly,
        sameSite: c.sameSite,
        expirationDate: c.expirationDate || null
      }))
    }
  };

  output.innerHTML = `<li>Sending policy text to summariser...</li>`;

  let policyOut = null;
  try {
    policyOut = await runPolicySummariser(policyJSON);
  } catch (e) {
    policyOut = { error: String(e.message || e) };
  }

  // Render for testing
  output.innerHTML = `
    <h3>Policy OUTPUT (from Summariser)</h3>
    <pre>${JSON.stringify(policyOut, null, 2).slice(0, 6000)}</pre>

    <h3>Cookies JSON (for Analyzer)</h3>
    <pre>${JSON.stringify(cookiesJSON, null, 2).slice(0, 3000)}</pre>
  `;
}

//   // Store globally (useful later)
//   window.__POLICY_JSON__ = policyJSON;
//   window.__COOKIES_JSON__ = cookiesJSON;

//   function downloadJSON(data, filename) {
//   const blob = new Blob([JSON.stringify(data, null, 2)], {
//     type: "application/json"
//   });
//   const url = URL.createObjectURL(blob);

//   const a = document.createElement("a");
//   a.href = url;
//   a.download = filename;
//   a.click();

//   URL.revokeObjectURL(url);
// }

//   // 🔹 Render for testing
//   output.innerHTML = `
//     <h3>Policy JSON (for Summarizer)</h3>
//     <pre>${JSON.stringify(policyJSON, null, 2).slice(0, 3000)}</pre>

//     <h3>Cookies JSON (for Analyzer)</h3>
//     <pre>${JSON.stringify(cookiesJSON, null, 2)}</pre>
//   `;
// }