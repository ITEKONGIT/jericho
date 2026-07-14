Java.perform(function() {
    console.log("[*] Universal Android Anti-Tamper Bypass Initialized");

    // --- 1. BLOCK ONLY SHOW, NOT CONSTRUCTION ---
    function blockShows() {
        try {
            var Dialog = Java.use('android.app.Dialog');
            // Do NOT block constructor; only block show
            Dialog.show.implementation = function() {
                console.log("[!] Dialog.show() blocked");
                return;
            };
            console.log("[+] Dialog.show blocked");
        } catch(e) {}

        try {
            var AlertDialog = Java.use('android.app.AlertDialog');
            AlertDialog.show.implementation = function() {
                console.log("[!] AlertDialog.show() blocked");
                return;
            };
            console.log("[+] AlertDialog.show blocked");
        } catch(e) {}

        try {
            var Builder = Java.use('android.app.AlertDialog$Builder');
            Builder.show.implementation = function() {
                console.log("[!] AlertDialog.Builder.show() blocked");
                return null;
            };
            console.log("[+] AlertDialog.Builder.show blocked");
        } catch(e) {}

        try {
            var PopupWindow = Java.use('android.widget.PopupWindow');
            PopupWindow.showAtLocation.implementation = function() {
                console.log("[!] PopupWindow.showAtLocation blocked");
                return;
            };
            console.log("[+] PopupWindow blocked");
        } catch(e) {}

        try {
            var Toast = Java.use('android.widget.Toast');
            Toast.show.implementation = function() {
                console.log("[!] Toast blocked");
                return;
            };
            console.log("[+] Toast blocked");
        } catch(e) {}
    }
    blockShows();

    // --- 2. HOOK OBFUSCATED CLASS th.d TO PREVENT DIALOG CREATION ---
    // Instead of blocking constructor, we can hook the run method of th.d$a
    // But we don't know the exact class name; we can try to find it at runtime.
    setTimeout(function() {
        // Hook all Runnables and check stack trace for th.d
        try {
            var Runnable = Java.use('java.lang.Runnable');
            Runnable.run.implementation = function() {
                var stack = Java.use('android.util.Log').getStackTraceString(Java.use('java.lang.Exception').$new());
                if (stack.indexOf("th.d") !== -1) {
                    console.log("[!] th.d Runnable.run() blocked");
                    return; // prevent execution
                }
                return this.run();
            };
            console.log("[+] Runnable.run hooked for th.d blocking");
        } catch(e) {
            console.log("[-] Runnable hook failed: " + e);
        }
    }, 1000);

    // --- 3. PREVENT EXIT AND FINISH ---
    try {
        var System = Java.use('java.lang.System');
        System.exit.implementation = function(code) {
            console.log("[!] System.exit(" + code + ") blocked!");
            return;
        };
        console.log("[+] System.exit blocked");
    } catch(e) {}

    try {
        var Activity = Java.use('android.app.Activity');
        Activity.finish.implementation = function() {
            console.log("[!] Activity.finish() blocked");
            return;
        };
        Activity.finishAffinity.implementation = function() {
            console.log("[!] Activity.finishAffinity() blocked");
            return;
        };
        console.log("[+] Activity.finish blocked");
    } catch(e) {}

    // --- 4. HANDLE WINDOW MANAGER ---
    try {
        var WindowManagerGlobal = Java.use('android.view.WindowManagerGlobal');
        var overloads = WindowManagerGlobal.removeView.overloads;
        overloads.forEach(function(overload) {
            overload.implementation = function() {
                return this.removeView.apply(this, arguments);
            };
        });
        console.log("[+] WindowManager hooked");
    } catch(e) {}

    // --- 5. SSL BYPASS ---
    try {
        var CertificatePinner = Java.use('okhttp3.CertificatePinner');
        CertificatePinner.check.overload('java.lang.String', 'java.util.List').implementation = function(hostname, certs) {
            console.log("[+] SSL bypass for " + hostname);
            return;
        };
        console.log("[+] OkHttp bypassed");
    } catch(e) {}

    try {
        var TrustManager = Java.use('javax.net.ssl.X509TrustManager');
        TrustManager.checkServerTrusted.overload('[Ljava.security.cert.X509Certificate;', 'java.lang.String').implementation = function(chain, authType) {
            console.log("[+] TrustManager bypassed");
            return;
        };
        console.log("[+] TrustManager bypassed");
    } catch(e) {}

    // --- 6. NETWORK MONITOR ---
    try {
        var RealCall = Java.use('okhttp3.internal.connection.RealCall');
        RealCall.execute.implementation = function() {
            var request = this.request();
            console.log("[HTTP] " + request.method() + " " + request.url());
            var response = this.execute();
            console.log("[RESPONSE] " + response.code());
            return response;
        };
        console.log("[+] Network monitor active");
    } catch(e) {}

    console.log("[*] All hooks installed. App should stay open.");
});