l = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "+", "/"]

function n_(t) {
    var n;
    n = f(t.toString(), "binary");
    return u(n)
}
function a(t) {
    return l[t >> 18 & 63] + l[t >> 12 & 63] + l[t >> 6 & 63] + l[63 & t]
}
function s(t, e, n) {
    for (var r, i = [], o = e; o < n; o += 3)
        r = (t[o] << 16 & 16711680) + (t[o + 1] << 8 & 65280) + (255 & t[o + 2]),
            i.push(a(r));
    return i.join("")
}
function u(t) {
    for (var e, n = t.length, r = n % 3, i = "", o = [], a = 16383, u = 0, c = n - r; u < c; u += a)
        o.push(s(t, u, u + a > c ? c : u + a));
    return 1 === r ? (e = t[n - 1],
        i += l[e >> 2],
        i += l[e << 4 & 63],
        i += "==") : 2 === r && (e = (t[n - 2] << 8) + t[n - 1],
        i += l[e >> 10],
        i += l[e >> 4 & 63],
        i += l[e << 2 & 63],
        i += "="),
        o.push(i),
        o.join("")
}
function K(t, e, n, r) {
    for (var i = 0; i < r && !(i + n >= e.length || i >= t.length); ++i)
        e[i + n] = t[i];
    return i
}
function W(t) {
    for (var e = [], n = 0; n < t.length; ++n)
        e.push(255 & t.charCodeAt(n));
    return e
}
function t_(t, e, n, r) {
    return K(W(e), t, 0, r)
}
function f(e, n) {
    var r = e.length,
      t = new Uint8Array(r);
    var i = t_(t, e, n, r);
    return t
}
function v_(n) {
    return n_(encodeURIComponent(n)["replace"](/%([0-9A-F]{2})/g, function (a, n) {
        return String["fromCharCode"]("0x" + n)
    }))
}
function k_(a, n) {
    //n || (n = s()),
    a = a["split"]("");
    for (var t = a["length"], e = n["length"], r = "charCodeAt", i = 0; i < t; i++)
        //a[i] = m_(a[i][r](0) ^ n[(i + 10) % e][r](0));
        a[i] = String["fromCharCode"](a[i][r](0) ^ n[(i + 10) % e][r](0));
    return a["join"]("")
}

function getLoginAnalysis (synct) {
    var g = new Date() - 1000 * synct;
    var e = new Date() - g - 1515125653845;
    var S = 1;
    m_1 = "@#/account/signinForm";
    m_2 = m_1 + "@#" + e;
    m_3 = m_2 + "@#" + S;
    var b = "00000008d78d46a";
    return v_(k_(m_3, b))
}

function getAnalysis (p_str, url, synct) {
    var g = new Date() - 1000 * synct;
    var e = new Date() - g - 1515125653845;
    var S = 1;
    m_0 = v_(p_str);
    m_1 = m_0 + "@#" + url.replace("https://api.qimai.cn", "");
    m_2 = m_1 + "@#" + e;
    m_3 = m_2 + "@#" + S;
    var b = "00000008d78d46a";
    return v_(k_(m_3, b))
}

// console.log(getAnalysis('26022', 'https://api.qimai.cn/addapp/comment', 1566966828.687));
