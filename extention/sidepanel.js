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

async function scanForPolicyLinks() {
  const [tab] = await chrome.tabs.query({
    active: true,
    currentWindow: true
  });

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
async function runPolicySummariser(policyJSON) {
  const res = await fetch("http://localhost:8000/policy/analyze", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(policyJSON)
  });

  if (!res.ok) {
    const txt = await res.text();
    throw new Error(`Backend ${res.status}: ${txt}`);
  }

  return await res.json(); // this is your output.json
}

function renderPolicyOutput(policyOut) {
  if (!policyOut) {
    return "<p>No policy analysis available.</p>";
  }

  if (policyOut.error) {
    return `<p style="color:red;">Error: ${policyOut.error}</p>`;
  }

  const {
    summary_simple,
    key_takeaways = [],
    policy_risk_score,
    risk_level
  } = policyOut;

  const riskColor =
    risk_level === "High" ? "#d32f2f" :
    risk_level === "Medium" ? "#f9a825" :
    "#2e7d32";

  return `
    <div class="policy-box">

      <h4>Summary</h4>
      <p>${summary_simple || "No summary available."}</p>

      <h4>Key Takeaways</h4>
      <ul>
        ${key_takeaways.map(k => `<li>${k}</li>`).join("")}
      </ul>

      <h4>Risk Assessment</h4>
      <p>
        <strong>Risk Level:</strong>
        <span style="color:${riskColor}; font-weight:600;">
          ${risk_level || "Unknown"}
        </span>
      </p>
      <p><strong>Risk Score:</strong> ${policy_risk_score ?? "N/A"} / 10</p>

    </div>
  `;
}

function buildCookieAnalyzerPayload(url, browserCookies, cmpInfo) {
  const siteDomain = new URL(url).hostname;

const normalizedCookies = browserCookies.map(c => {
    let expiryDays = 0;

    if (c.expirationDate) {
      const now = Date.now() / 1000;
      expiryDays = Math.max(
        0,
        Math.round((c.expirationDate - now) / (60 * 60 * 24))
      );
    }

    return {
      name: c.name,
      domain: c.domain,
      expiry_days: expiryDays,
      secure: !!c.secure,
      sameSite: c.sameSite || "None"
    };
  });

  // v1 conservative consent inference (OK for now)
  const consentUI = {
    accept_clicks: 1,
    reject_clicks: 2,
    manage_preferences_visible: true,
    consent_required_to_proceed: false,
    categories: [
      {
        label: "Analytics",
        description: "Analytics cookies",
        prechecked: true
      }
    ]
  };

  return {
    site_domain: siteDomain,
    cookies: normalizedCookies,
    consent_ui: consentUI,
    cmp_detected:
      Object.keys(cmpInfo.providers)
        .filter(k => cmpInfo.providers[k])
        .join(",") || "unknown"
  };
}
async function runCookieAnalyzer(cookiePayload) {
  const res = await fetch("http://127.0.0.1:8000/cookies/analyze", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(cookiePayload)
  });

  if (!res.ok) {
    const txt = await res.text();
    throw new Error(`Cookie backend ${res.status}: ${txt}`);
  }

  return await res.json();
}



// ================= BUILD JSON + RENDER =================
async function buildAndRenderJSON(url, text, domCookies, browserCookies, cmpInfo) {

  // 🔹 Policy payload
  const policyJSON = {
    url: url,
    raw_text: text,
    captured_at: new Date().toISOString()
  };

  // 🔹 Cookie analyzer payload (MATCHES BACKEND SCHEMA)
  const cookieAnalyzerPayload = buildCookieAnalyzerPayload(
    url,
    browserCookies,
    cmpInfo
  );

  output.innerHTML = `<li>Sending data to analyzers...</li>`;

  // --- POLICY ---
  let policyOut = null;
  try {
    policyOut = await runPolicySummariser(policyJSON);
  } catch (e) {
    policyOut = { error: String(e.message || e) };
  }

  // --- COOKIES ---
  let cookieOut = null;
  try {
    cookieOut = await runCookieAnalyzer(cookieAnalyzerPayload);
  } catch (e) {
    cookieOut = { error: String(e.message || e) };
  }

  // --- RENDER ---
  output.innerHTML = `
    <h3>Policy Analysis</h3>
    ${renderPolicyOutput(policyOut)}

    <h3>Cookie Analysis</h3>

    ${
      cookieOut?.summary
        ? `<p><b>Summary:</b> ${cookieOut.summary}</p>`
        : `<p style="color:#999;">No cookie summary available.</p>`
    }

    <p><b>Risk Level:</b> ${cookieOut?.risk_level || "Unknown"}</p>

    <h4>Flags</h4>
    <ul>
      ${(cookieOut?.flags || []).map(f => `<li>${f}</li>`).join("")}
    </ul>

    <details style="margin-top:12px;">
      <summary><b>Technical Details</b></summary>
      <pre>${JSON.stringify(cookieOut, null, 2).slice(0, 4000)}</pre>
    </details>
  `;
}

document
  .getElementById("openDashboard")
  .addEventListener("click", () => {
    chrome.tabs.create({
      url: "http://localhost:8501"
    });
  });
