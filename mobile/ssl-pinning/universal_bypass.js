// Jericho Framework: Universal TrustManagerImpl Hook
Java.perform(function() {
    var TrustManagerImpl = Java.use('com.android.org.conscrypt.TrustManagerImpl');
    TrustManagerImpl.verifyChain.implementation = function(a, b, c, d, e, f) {
        console.log("[+] Hooking TrustManagerImpl: Bypassing SSL Pinning");
        return a;
    };
    console.log("[+] Universal SSL Pinning bypass loaded");
});
