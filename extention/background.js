chrome.action.onClicked.addListener(async (tab) => {
  await chrome.sidePanel.open({ tabId: tab.id });
});

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {

  // 🔹 Fetch HTML privacy policy
  if (msg.type === "FETCH_POLICY") {
    fetch(msg.url)
      .then(res => res.text())
      .then(html => sendResponse({ html }))
      .catch(err => sendResponse({ error: err.message }));

    return true; // async response
  }

  // 🔹 Fetch PDF as bytes
  if (msg.type === "FETCH_PDF") {
    fetch(msg.url)
      .then(res => res.arrayBuffer())
      .then(buffer => {
        sendResponse({
          bytes: Array.from(new Uint8Array(buffer))
        });
      })
      .catch(err => sendResponse({ error: err.message }));

    return true;
  }

  // 🔹 Fetch browser cookies
  if (msg.type === "GET_COOKIES") {
    chrome.cookies.getAll({ url: msg.url }, (cookies) => {
      sendResponse({ cookies });
    });

    return true;
  }
});


