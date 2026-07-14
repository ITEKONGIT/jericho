// Safely find the 'connect' function across all loaded modules
var connectFunc = null;

// Enumerate modules to find 'connect'
Process.enumerateModules().forEach(function(mod) {
    if (mod.name.indexOf("libc") !== -1) {
        mod.enumerateExports().forEach(function(exp) {
            if (exp.name === "connect") {
                connectFunc = exp.address;
            }
        });
    }
});

if (connectFunc) {
    Interceptor.attach(connectFunc, {
        onEnter: function (args) {
            console.log("[+] connect() intercepted at: " + connectFunc);
            // args[1] is the sockaddr struct
            var sockaddr = args[1];
            // Read first 16 bytes of sockaddr
            var data = Memory.readByteArray(sockaddr, 16);
            console.log(hexdump(data, { length: 16, header: false }));
        }
    });
} else {
    console.log("[-] Could not find 'connect'. Retrying after 2 seconds...");
    // Fallback: If not found, it might be loaded dynamically later
}