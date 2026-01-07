// ================= PDF.js SETUP =================
pdfjsLib.GlobalWorkerOptions.workerSrc =
  chrome.runtime.getURL("lib/pdf/pdf.worker.js");

// ================= DOM ELEMENTS =================
const btn = document.getElementById("readText");
const output = document.getElementById("output");

// ================= MAIN BUTTON =================
btn.addEventListener("click", async () => {
  output.innerHTML = "<li>Scanning page for policy links...</li>";

  const [tab] = await chrome.tabs.query({
    active: true,
    currentWindow: true
  });

  const [{ result }] = await chrome.scripting.executeScript({
    target: { tabId: tab.id },
    func: () => {
      return [...document.querySelectorAll("a")]
        .map(a => ({
          text: a.innerText.trim(),
          href: a.href
        }))
        .filter(link =>
          link.text &&
          /privacy|cookie|terms|policy|legal/i.test(link.text)
        );
    }
  });

  output.innerHTML = "";

  if (!result || result.length === 0) {
    output.innerHTML = "<li>No policy links found</li>";
    return;
  }

  result.forEach(link => {
    const li = document.createElement("li");
    const a = document.createElement("a");

    a.href = "#";
    a.textContent = link.text;

    a.addEventListener("click", () => {
      handlePolicyLink(link.href);
    });

    li.appendChild(a);
    output.appendChild(li);
  });
});

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
    (response) => {
      if (!response || response.error) {
        output.innerHTML = "<li>Error loading policy</li>";
        return;
      }

      const parser = new DOMParser();
      const doc = parser.parseFromString(response.html, "text/html");
      const text = doc.body.innerText;

      renderResult(url, text, domCookies, browserCookies, cmpInfo);
    }
  );
}

// ================= PDF POLICY =================
function fetchPDF(url, domCookies, browserCookies, cmpInfo) {
  chrome.runtime.sendMessage(
    { type: "FETCH_PDF", url },
    async (response) => {
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

        renderResult(url, text, domCookies, browserCookies, cmpInfo);
      } catch (err) {
        output.innerHTML = `<li>PDF parse error: ${err.message}</li>`;
      }
    }
  );
}

// ================= CMP DETECTION (SYNC & SAFE) =================
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

// ================= RENDER RESULT =================
function renderResult(url, text, domCookies, browserCookies, cmpInfo) {
  output.innerHTML = `
    <h3>URL</h3>
    <pre>${url}</pre>

    <h3>CMP Info</h3>
    <pre>${JSON.stringify(cmpInfo, null, 2)}</pre>

    <h3>DOM Cookies (${domCookies.length})</h3>
    <pre>${JSON.stringify(domCookies, null, 2)}</pre>

    <h3>Browser Cookies (${browserCookies.length})</h3>
    <pre>${JSON.stringify(browserCookies, null, 2)}</pre>

    <h3>Policy Text (Preview)</h3>
    <pre>${text.slice(0, 2000)}</pre>
  `;
}
