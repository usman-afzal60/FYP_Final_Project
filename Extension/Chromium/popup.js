const authorizeButton = document.getElementById("authorize");
const signOutButton = document.getElementById("sign_out");
const resultDiv = document.getElementById("result");
const showReportsBtn = document.getElementById("show_reports");

authorizeButton.addEventListener("click", authorize);
signOutButton.addEventListener("click", signOut);

function updateUI(signedIn) {
  authorizeButton.hidden = signedIn;
  signOutButton.hidden = !signedIn;

}

document.addEventListener("DOMContentLoaded", function () {
  chrome.storage.local.get(["access_token"], function (result) {
    updateUI(!!result.access_token);
    if (result.access_token) {
      getEmails();
    }
  });
});

chrome.storage.onChanged.addListener(function (changes, areaName) {
  if (areaName === "local" && changes.access_token) {
    if (changes.access_token.newValue) {
      updateUI(true);
      getEmails();
    } else {
      updateUI(false);
    }
  }
});

function showOverlay() {
  document.getElementById("overlay").style.display = "block";
}

function hideOverlay() {
  document.getElementById("overlay").style.display = "none";
}

async function authorize() {
  try {
    const token = await new Promise((resolve, reject) => {
      chrome.identity.getAuthToken(
        {
          interactive: true,
          scopes: ["https://www.googleapis.com/auth/gmail.readonly"],
        },
        function (token) {
          if (chrome.runtime.lastError) {
            reject(chrome.runtime.lastError);
          } else {
            resolve(token);
          }
        }
      );
    });

    // Save the OAuth token to local storage first
    chrome.storage.local.set({ access_token: token }, function () {
      // Then send the token to the backend
      sendOAuthTokenToBackend(token);

      updateUI(true);
      getEmails();
    });

  } catch (error) {
    if (error.message === "OAuth2 not granted or revoked.") {
      alert("Please grant the required permissions for the extension to work.");
    } else {
      console.error(error);
    }
  }
}


async function signOut() {
  try {
    const result = await new Promise((resolve, reject) => {
      chrome.storage.local.get(["access_token"], function (result) {
        if (chrome.runtime.lastError) {
          reject(chrome.runtime.lastError);
        } else {
          resolve(result);
        }
      });
    });

    if (result.access_token) {
      await fetch(
        `https://accounts.google.com/o/oauth2/revoke?token=${result.access_token}`
      );

      chrome.identity.removeCachedAuthToken(
        { token: result.access_token },
        function () {
          chrome.storage.local.remove("access_token", function () {
            // Use a callback function to ensure that updateUI(false) is called after the access token is removed
            if (chrome.runtime.lastError) {
              console.error(chrome.runtime.lastError);
            } else {
              updateUI(false);
            }
          });
        }
      );
    }
  } catch (error) {
    console.error("Error revoking token:", error);
  }
}

function getEmailDetails(accessToken, messageId, callback) {
  fetch(`https://www.googleapis.com/gmail/v1/users/me/messages/${messageId}`, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  })
    .then((response) => response.json())
    .then((data) => {
      callback(data);
    })
    .catch((error) => {
      console.error(error);
      callback(null);
    });
}

let emailsLoaded = false;
let selectedEmails = [];

function updateSelectedEmails(event) {
  const emailItem = event.target.parentElement.parentElement;
  const emailId = emailItem.getAttribute("data-id");

  if (event.target.checked) {
    selectedEmails.push(emailId);
  } else {
    selectedEmails = selectedEmails.filter((id) => id !== emailId);
  }
}

function getEmails() {
  if (emailsLoaded) {
    return;
  }
  showOverlay();
  chrome.storage.local.get(["access_token"], function (result) {
    if (result.access_token) {
      fetch("https://www.googleapis.com/gmail/v1/users/me/messages", {
        headers: {
          Authorization: `Bearer ${result.access_token}`,
        },
      })
        .then((response) => response.json())
        .then((data) => {
          resultDiv.innerHTML = "";
          let emailPromises = [];
          for (let item of data.messages) {
            emailPromises.push(
              new Promise((resolve) => {
                getEmailDetails(result.access_token, item.id, (email) => {
                  if (email) {
                    let emailItem = document.createElement("div");
                    emailItem.className = "email-item";

                    // Create the checkbox element
                    let checkbox = document.createElement("input");
                    checkbox.type = "checkbox";
                    checkbox.id = item.id; // Set the id attribute to the email ID
                    emailItem.appendChild(checkbox);

                    let subject = email.payload.headers.find(
                      (header) => header.name === "Subject"
                    ).value;
                    let from = email.payload.headers.find(
                      (header) => header.name === "From"
                    ).value;

                    emailItem.innerHTML += `<strong>${from}</strong><br>${subject}`;
                    resultDiv.appendChild(emailItem);

                    let emailInfo = document.createElement("div");
                    emailInfo.className = "email-info";
                    emailInfo.id = item.id;
                    emailItem.appendChild(emailInfo);
                  }
                  resolve();
                });
              })
            );
          }
          Promise.all(emailPromises).then(() => {
            // Add event listeners for checkboxes
            document.querySelectorAll(".email-item input[type=checkbox]").forEach(checkbox => {
              checkbox.addEventListener("change", updateSelectedEmails);
            });

            document.getElementById("send_emails").hidden = false;
            hideOverlay();
            emailsLoaded = true; // Set the variable to true after loading the emails
            showReportsBtn.hidden = false;
            thisToken = chrome.storage.local.get(["access_token"]);
            showReportsBtn.onclick = function () {
              window.open("http://139.59.80.155:3000", "_blank");
              console.log("Opening Reporting Panel")
            }
          });
        })
        .catch((error) => {
          console.error(error);
          resultDiv.innerHTML = "An error occurred while fetching emails.";
          hideOverlay();
        });
    }
  });
}


async function sendSelectedEmails() {
  let selectedCheckboxes = Array.from(
    document.querySelectorAll(".email-item input[type=checkbox]:checked")

  );

  chrome.storage.local.get(["access_token"], async function (result) {
    if (result.access_token) {
      try {
        for (const checkbox of selectedCheckboxes) {
          await new Promise((resolve, reject) => {
            let id = checkbox.id; // Get the email ID from the checkbox
            sendEmailIdToBackend(id)
              .then((data) => {
                let emailItem = checkbox.closest(".email-item");


                if (emailItem) {
                  let statusSpan = document.createElement("span");
                  statusSpan.className = "status";
                  statusSpan.textContent = data;
                  // Find the div with the class 'email-info' and append the statusSpan to it
                  let emailInfoDiv = emailItem.querySelector(".email-info");
                  if (emailInfoDiv) {
                    emailInfoDiv.appendChild(statusSpan);
                    resolve();
                  } else {
                    reject(new Error("Failed to find email-info element."));
                  }
                } else {
                  reject(new Error("Failed to find email item."));
                }
              })
              .catch((error) => {
                console.error("Error sending email ID to backend:", error);
                reject(error);
              });
          });
        }
        alert("Selected email(s) have been sent for Analysis.");
      } catch (error) {
        console.error("An error occurred while analyzing emails:", error);
        alert("An error occurred while analyzing emails.");
      }
    }
  });
}

function sendEmailIdToBackend(emailId) {
  const backendUrl = "https://scanner.mailassure.tech/upload";

  return new Promise((resolve, reject) => {
    chrome.storage.local.get(["access_token"], function (result) {
      if (result.access_token) {
        fetch(backendUrl, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ email_id: emailId, token: result.access_token }),
        })
          .then((response) => {
            if (!response.ok) {
              reject(
                new Error(
                  `Network response was not ok: ${response.status} ${response.statusText}`
                )
              );
            } else {
              return response.text();
            }
          })
          .then((text) => {
            resolve(text);
          })
          .catch((error) => {
            console.error("There was a problem with the fetch operation:", error);
            reject(error);
          });
      } else {
        reject(new Error("Failed to get access_token from storage"));
      }
    });
  });
}

document
  .getElementById("send_emails")
  .addEventListener("click", sendSelectedEmails);