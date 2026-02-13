/*! coi-serviceworker v0.1.7 - Guido Zuidhof and contributors, licensed under MIT */
let coepCredentialless = false;
if (typeof window === 'undefined') {
    self.addEventListener("install", () => self.skipWaiting());
    self.addEventListener("activate", (event) => event.waitUntil(self.clients.claim()));

    self.addEventListener("fetch", function (event) {
        event.respondWith((async function () {
            if (event.request.cache === "only-if-cached" && event.request.mode !== "same-origin") {
                return;
            }

            const r = await fetch(event.request).catch(e => console.error(e));

            if (!r) {
                return r;
            }

            const headers = new Headers(r.headers);
            headers.set("Cross-Origin-Embedder-Policy",
                coepCredentialless ? "credentialless" : "require-corp"
            );
            if (!coepCredentialless) {
                headers.set("Cross-Origin-Resource-Policy", "cross-origin");
            }
            headers.set("Cross-Origin-Opener-Policy", "same-origin");

            return new Response(r.body, { status: r.status, statusText: r.statusText, headers });
        })());
    });
} else {
    (() => {
        const reloadedBySelf = window.sessionStorage.getItem("coiReloadedBySelf");
        window.sessionStorage.removeItem("coiReloadedBySelf");
        const coepDegrading = (reloadedBySelf == "coepdegrade");

        const needsCrossOriginIsolated = !crossOriginIsolated;
        const reloadToCheckCredentialless = false;
        if (!needsCrossOriginIsolated && !reloadToCheckCredentialless) {
            return;
        }

        if (!coepDegrading) {
            window.sessionStorage.setItem("coiReloadedBySelf", "coepdegrade");

            if (reloadToCheckCredentialless) {
                window.sessionStorage.setItem("coiCoepCredentialless", coepCredentialless.toString());
            }
        }

        let registration;
        navigator.serviceWorker.register(window.document.currentScript.src).then(
            (r) => {
                registration = r;
                if (!registration.active && !registration.installing && !registration.waiting) {
                    return;
                }
                return new Promise((resolve) => {
                    if (registration.active) return resolve();
                    const statusChangeListener = () => {
                        if (registration.active) {
                            resolve();
                            registration.removeEventListener("updatefound", statusChangeListener);
                        }
                    };
                    registration.addEventListener("updatefound", statusChangeListener);
                });
            },
            (err) => console.error("COOP/COEP Service Worker failed to register:", err)
        ).then(() => {
            if (!registration || !registration.active) {
                console.log("COOP/COEP Service Worker not loaded. Not reloading page.");
            }
            window.location.reload();
        });
    })();
}