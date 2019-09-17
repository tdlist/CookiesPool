var Myencrypter = Myencrypter || function (t, e) {
    var n = Object.create || function () {
        function t() {
        }

        return function (e) {
            var n;
            return t.prototype = e,
                n = new t,
                t.prototype = null,
                n
        }
    }()
        , r = {}
        , i = r.lib = {}
        , o = i.Base = function () {
        return {
            extend: function (t) {
                var e = n(this);
                return t && e.mixIn(t),
                e.hasOwnProperty("init") && this.init !== e.init || (e.init = function () {
                        e.$super.init.apply(this, arguments)
                    }
                ),
                    e.init.prototype = e,
                    e.$super = this,
                    e
            },
            create: function () {
                var t = this.extend();
                return t.init.apply(t, arguments),
                    t
            },
            init: function () {
            },
            mixIn: function (t) {
                for (var e in t)
                    t.hasOwnProperty(e) && (this[e] = t[e]);
                t.hasOwnProperty("toString") && (this.toString = t.toString)
            },
            clone: function () {
                return this.init.prototype.extend(this)
            }
        }
    }()
        , a = i.WordArray = o.extend({
        init: function (t, e) {
            t = this.words = t || [],
                this.sigBytes = void 0 != e ? e : 4 * t.length
        },
        toString: function (t) {
            return (t || u).stringify(this)
        },
        concat: function (t) {
            var e = this.words
                , n = t.words
                , r = this.sigBytes
                , i = t.sigBytes;
            if (this.clamp(),
            r % 4)
                for (var o = 0; o < i; o++) {
                    var a = n[o >>> 2] >>> 24 - o % 4 * 8 & 255;
                    e[r + o >>> 2] |= a << 24 - (r + o) % 4 * 8
                }
            else
                for (var o = 0; o < i; o += 4)
                    e[r + o >>> 2] = n[o >>> 2];
            return this.sigBytes += i,
                this
        },
        clamp: function () {
            var e = this.words
                , n = this.sigBytes;
            e[n >>> 2] &= 4294967295 << 32 - n % 4 * 8,
                e.length = t.ceil(n / 4)
        },
        clone: function () {
            var t = o.clone.call(this);
            return t.words = this.words.slice(0),
                t
        },
        random: function (e) {
            for (var n, r = [], i = 0; i < e; i += 4) {
                var o = function (e) {
                    var e = e
                        , n = 987654321
                        , r = 4294967295;
                    return function () {
                        n = 36969 * (65535 & n) + (n >> 16) & r,
                            e = 18e3 * (65535 & e) + (e >> 16) & r;
                        var i = (n << 16) + e & r;
                        return i /= 4294967296,
                        (i += .5) * (t.random() > .5 ? 1 : -1)
                    }
                }(4294967296 * (n || t.random()));
                n = 987654071 * o(),
                    r.push(4294967296 * o() | 0)
            }
            return new a.init(r, e)
        }
    })
        , s = r.enc = {}
        , u = s.Hex = {
        stringify: function (t) {
            for (var e = t.words, n = t.sigBytes, r = [], i = 0; i < n; i++) {
                var o = e[i >>> 2] >>> 24 - i % 4 * 8 & 255;
                r.push((o >>> 4).toString(16)),
                    r.push((15 & o).toString(16))
            }
            return r.join("")
        },
        parse: function (t) {
            for (var e = t.length, n = [], r = 0; r < e; r += 2)
                n[r >>> 3] |= parseInt(t.substr(r, 2), 16) << 24 - r % 8 * 4;
            return new a.init(n, e / 2)
        }
    }
        , c = s.Latin1 = {
        stringify: function (t) {
            for (var e = t.words, n = t.sigBytes, r = [], i = 0; i < n; i++) {
                var o = e[i >>> 2] >>> 24 - i % 4 * 8 & 255;
                r.push(String.fromCharCode(o))
            }
            return r.join("")
        },
        parse: function (t) {
            for (var e = t.length, n = [], r = 0; r < e; r++)
                n[r >>> 2] |= (255 & t.charCodeAt(r)) << 24 - r % 4 * 8;
            return new a.init(n, e)
        }
    }
        , l = s.Utf8 = {
        stringify: function (t) {
            try {
                return decodeURIComponent(escape(c.stringify(t)))
            } catch (t) {
                throw new Error("Malformed UTF-8 data")
            }
        },
        parse: function (t) {
            return c.parse(unescape(encodeURIComponent(t)))
        }
    }
        , f = i.BufferedBlockAlgorithm = o.extend({
        reset: function () {
            this._data = new a.init,
                this._nDataBytes = 0
        },
        _append: function (t) {
            "string" == typeof t && (t = l.parse(t)),
                this._data.concat(t),
                this._nDataBytes += t.sigBytes
        },
        _process: function (e) {
            var n = this._data
                , r = n.words
                , i = n.sigBytes
                , o = this.blockSize
                , s = 4 * o
                , u = i / s;
            u = e ? t.ceil(u) : t.max((0 | u) - this._minBufferSize, 0);
            var c = u * o
                , l = t.min(4 * c, i);
            if (c) {
                for (var f = 0; f < c; f += o)
                    this._doProcessBlock(r, f);
                var d = r.splice(0, c);
                n.sigBytes -= l
            }
            return new a.init(d, l)
        },
        clone: function () {
            var t = o.clone.call(this);
            return t._data = this._data.clone(),
                t
        },
        _minBufferSize: 0
    })
        , d = (i.Hasher = f.extend({
        cfg: o.extend(),
        init: function (t) {
            this.cfg = this.cfg.extend(t),
                this.reset()
        },
        reset: function () {
            f.reset.call(this),
                this._doReset()
        },
        update: function (t) {
            return this._append(t),
                this._process(),
                this
        },
        finalize: function (t) {
            return t && this._append(t),
                this._doFinalize()
        },
        blockSize: 16,
        _createHelper: function (t) {
            return function (e, n) {
                return new t.init(n).finalize(e)
            }
        },
        _createHmacHelper: function (t) {
            return function (e, n) {
                return new d.HMAC.init(t, n).finalize(e)
            }
        }
    }),
        r.algo = {});
    return r
}(Math);
(function () {
    function e(t, e, n) {
        for (var r = [], o = 0, a = 0; a < e; a++)
            if (a % 4) {
                var s = n[t.charCodeAt(a - 1)] << a % 4 * 2
                    , u = n[t.charCodeAt(a)] >>> 6 - a % 4 * 2;
                r[o >>> 2] |= (s | u) << 24 - o % 4 * 8,
                    o++
            }
        return i.create(r, o)
    }

    var n = Myencrypter
        , r = n.lib
        , i = r.WordArray
        , o = n.enc;
    o.Base64 = {
        stringify: function (t) {
            var e = t.words
                , n = t.sigBytes
                , r = this._map;
            t.clamp();
            for (var i = [], o = 0; o < n; o += 3)
                for (var a = e[o >>> 2] >>> 24 - o % 4 * 8 & 255, s = e[o + 1 >>> 2] >>> 24 - (o + 1) % 4 * 8 & 255, u = e[o + 2 >>> 2] >>> 24 - (o + 2) % 4 * 8 & 255, c = a << 16 | s << 8 | u, l = 0; l < 4 && o + .75 * l < n; l++)
                    i.push(r.charAt(c >>> 6 * (3 - l) & 63));
            var f = r.charAt(64);
            if (f)
                for (; i.length % 4;)
                    i.push(f);
            return i.join("")
        },
        parse: function (t) {
            var n = t.length
                , r = this._map
                , i = this._reverseMap;
            if (!i) {
                i = this._reverseMap = [];
                for (var o = 0; o < r.length; o++)
                    i[r.charCodeAt(o)] = o
            }
            var a = r.charAt(64);
            if (a) {
                var s = t.indexOf(a);
                -1 !== s && (n = s)
            }
            return e(t, n, i)
        },
        _map: "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="
    }
})();
Myencrypter.lib.Cipher || function (e) {
    var n = Myencrypter
        , r = n.lib
        , i = r.Base
        , o = r.WordArray
        , a = r.BufferedBlockAlgorithm
        , s = n.enc
        , u = (s.Utf8, s.Base64)
        , c = n.algo
        , l = c.EvpKDF
        , f = r.Cipher = a.extend({
        cfg: i.extend(),
        createEncryptor: function (t, e) {
            return this.create(this._ENC_XFORM_MODE, t, e)
        },
        createDecryptor: function (t, e) {
            return this.create(this._DEC_XFORM_MODE, t, e)
        },
        init: function (t, e, n) {
            this.cfg = this.cfg.extend(n),
                this._xformMode = t,
                this._key = e,
                this.reset()
        },
        reset: function () {
            a.reset.call(this),
                this._doReset()
        },
        process: function (t) {
            return this._append(t),
                this._process()
        },
        finalize: function (t) {
            return t && this._append(t),
                this._doFinalize()
        },
        keySize: 4,
        ivSize: 4,
        _ENC_XFORM_MODE: 1,
        _DEC_XFORM_MODE: 2,
        _createHelper: function () {
            function t(t) {
                return "string" == typeof t ? k : g
            }

            return function (e) {
                return {
                    encrypt: function (n, r, i) {
                        return t(r).encrypt(e, n, r, i)
                    },
                    decrypt: function (n, r, i) {
                        return t(r).decrypt(e, n, r, i)
                    }

                }
            }
        }()
    })
        , d = (r.StreamCipher = f.extend({
        _doFinalize: function () {
            return this._process(!0)
        },
        blockSize: 1
    }),
        n.mode = {})
        , h = r.BlockCipherMode = i.extend({
        createEncryptor: function (t, e) {
            return this.Encryptor.create(t, e)
        },
        createDecryptor: function (t, e) {
            return this.Decryptor.create(t, e)
        },
        init: function (t, e) {
            this._cipher = t,
                this._iv = e
        }
    })
        , p = d.CBC = function () {
        function t(t, n, r) {
            var i = this._iv;
            if (i) {
                var o = i;
                this._iv = e
            } else
                var o = this._prevBlock;
            for (var a = 0; a < r; a++)
                t[n + a] ^= o[a]
        }

        var n = h.extend();
        return n.Encryptor = n.extend({
            processBlock: function (e, n) {
                var r = this._cipher
                    , i = r.blockSize;
                t.call(this, e, n, i),
                    r.encryptBlock(e, n),
                    this._prevBlock = e.slice(n, n + i)
            }
        }),
            n.Decryptor = n.extend({
                processBlock: function (e, n) {
                    var r = this._cipher
                        , i = r.blockSize
                        , o = e.slice(n, n + i);
                    r.decryptBlock(e, n),
                        t.call(this, e, n, i),
                        this._prevBlock = o
                }
            }),
            n
    }()
        , m = n.pad = {}
        , y = m.Pkcs7 = {
        pad: function (t, e) {
            for (var n = 4 * e, r = n - t.sigBytes % n, i = r << 24 | r << 16 | r << 8 | r, a = [], s = 0; s < r; s += 4)
                a.push(i);
            var u = o.create(a, r);
            t.concat(u)
        },
        unpad: function (t) {
            var e = 255 & t.words[t.sigBytes - 1 >>> 2];
            t.sigBytes -= e
        }
    }
        , _ = (r.BlockCipher = f.extend({
        cfg: f.cfg.extend({
            mode: p,
            padding: y
        }),
        reset: function () {
            f.reset.call(this);
            var t = this.cfg
                , e = t.iv
                , n = t.mode;
            if (this._xformMode == this._ENC_XFORM_MODE)
                var r = n.createEncryptor;
            else {
                var r = n.createDecryptor;
                this._minBufferSize = 1
            }
            this._mode && this._mode.__creator == r ? this._mode.init(this, e && e.words) : (this._mode = r.call(n, this, e && e.words),
                this._mode.__creator = r)
        },
        _doProcessBlock: function (t, e) {
            this._mode.processBlock(t, e)
        },
        _doFinalize: function () {
            var t = this.cfg.padding;
            if (this._xformMode == this._ENC_XFORM_MODE) {
                t.pad(this._data, this.blockSize);
                var e = this._process(!0)
            } else {
                var e = this._process(!0);
                t.unpad(e)
            }
            return e
        },
        blockSize: 4
    }),
        r.CipherParams = i.extend({
            init: function (t) {
                this.mixIn(t)
            },
            toString: function (t) {
                return (t || this.formatter).stringify(this)
            }
        }))
        , v = n.format = {}
        , b = v.OpenSSL = {
        stringify: function (t) {
            var e = t.ciphertext
                , n = t.salt;
            if (n)
                var r = o.create([1398893684, 1701076831]).concat(n).concat(e);
            else
                var r = e;
            return r.toString(u)
        },
        parse: function (t) {
            var e = u.parse(t)
                , n = e.words;
            if (1398893684 == n[0] && 1701076831 == n[1]) {
                var r = o.create(n.slice(2, 4));
                n.splice(0, 4),
                    e.sigBytes -= 16
            }
            return _.create({
                ciphertext: e,
                salt: r
            })
        }
    }
        , g = r.SerializableCipher = i.extend({
        cfg: i.extend({
            format: b
        }),
        encrypt: function (t, e, n, r) {
            r = this.cfg.extend(r);
            var i = t.createEncryptor(n, r)
                , o = i.finalize(e)
                , a = i.cfg;
            return _.create({
                ciphertext: o,
                key: n,
                iv: a.iv,
                algorithm: t,
                mode: a.mode,
                padding: a.padding,
                blockSize: t.blockSize,
                formatter: r.format
            })
        },
        decrypt: function (t, e, n, r) {
            return r = this.cfg.extend(r),
                e = this._parse(e, r.format),
                t.createDecryptor(n, r).finalize(e.ciphertext)
        },
        _parse: function (t, e) {
            return "string" == typeof t ? e.parse(t, this) : t
        }
    })
        , w = n.kdf = {}
        , M = w.OpenSSL = {
        execute: function (t, e, n, r) {
            r || (r = o.random(8));
            // var i = l.create({
            //     keySize: e + n
            // }).compute(t, r)
            var i = Myencrypter.EvpKDF(t, r, {keySize: e + n})
                , a = o.create(i.words.slice(e), 4 * n);
            return i.sigBytes = 4 * e,
                _.create({
                    key: i,
                    iv: a,
                    salt: r
                })
        }
    }
        , k = r.PasswordBasedCipher = g.extend({
        cfg: g.cfg.extend({
            kdf: M
        }),
        encrypt: function (t, e, n, r) {
            r = this.cfg.extend(r);
            var i = r.kdf.execute(n, t.keySize, t.ivSize);
            r.iv = i.iv;
            var o = g.encrypt.call(this, t, e, i.key, r);
            return o.mixIn(i),
                o
        },
        decrypt: function (t, e, n, r) {
            r = this.cfg.extend(r),
                e = this._parse(e, r.format);
            var i = r.kdf.execute(n, t.keySize, t.ivSize, e.salt);
            return r.iv = i.iv,
                g.decrypt.call(this, t, e, i.key, r)
        }
    })
}();
(function () {
    var e = Myencrypter
        , n = e.lib
        , r = n.WordArray
        , i = n.Hasher
        , o = e.algo
        , a = []
        , s = o.SHA1 = i.extend({
        _doReset: function () {
            this._hash = new r.init([1732584193, 4023233417, 2562383102, 271733878, 3285377520])
        },
        _doProcessBlock: function (t, e) {
            for (var n = this._hash.words, r = n[0], i = n[1], o = n[2], s = n[3], u = n[4], c = 0; c < 80; c++) {
                if (c < 16)
                    a[c] = 0 | t[e + c];
                else {
                    var l = a[c - 3] ^ a[c - 8] ^ a[c - 14] ^ a[c - 16];
                    a[c] = l << 1 | l >>> 31
                }
                var f = (r << 5 | r >>> 27) + u + a[c];
                f += c < 20 ? 1518500249 + (i & o | ~i & s) : c < 40 ? 1859775393 + (i ^ o ^ s) : c < 60 ? (i & o | i & s | o & s) - 1894007588 : (i ^ o ^ s) - 899497514,
                    u = s,
                    s = o,
                    o = i << 30 | i >>> 2,
                    i = r,
                    r = f
            }
            n[0] = n[0] + r | 0,
                n[1] = n[1] + i | 0,
                n[2] = n[2] + o | 0,
                n[3] = n[3] + s | 0,
                n[4] = n[4] + u | 0
        },
        _doFinalize: function () {
            var t = this._data
                , e = t.words
                , n = 8 * this._nDataBytes
                , r = 8 * t.sigBytes;
            return e[r >>> 5] |= 128 << 24 - r % 32,
                e[14 + (r + 64 >>> 9 << 4)] = Math.floor(n / 4294967296),
                e[15 + (r + 64 >>> 9 << 4)] = n,
                t.sigBytes = 4 * e.length,
                this._process(),
                this._hash
        },
        clone: function () {
            var t = i.clone.call(this);
            return t._hash = this._hash.clone(),
                t
        }
    });
    e.SHA1 = i._createHelper(s);
    e.HmacSHA1 = i._createHmacHelper(s)
})();
(function (e) {
    function n(t, e, n, r, i, o, a) {
        var s = t + (e & n | ~e & r) + i + a;
        return (s << o | s >>> 32 - o) + e
    }

    function r(t, e, n, r, i, o, a) {
        var s = t + (e & r | n & ~r) + i + a;
        return (s << o | s >>> 32 - o) + e
    }

    function i(t, e, n, r, i, o, a) {
        var s = t + (e ^ n ^ r) + i + a;
        return (s << o | s >>> 32 - o) + e
    }

    function o(t, e, n, r, i, o, a) {
        var s = t + (n ^ (e | ~r)) + i + a;
        return (s << o | s >>> 32 - o) + e
    }

    var a = Myencrypter
        , s = a.lib
        , u = s.WordArray
        , c = s.Hasher
        , l = a.algo
        , f = [];
    !function () {
        for (var t = 0; t < 64; t++)
            f[t] = 4294967296 * e.abs(e.sin(t + 1)) | 0
    }();
    var d = l.MD5 = c.extend({
        _doReset: function () {
            this._hash = new u.init([1732584193, 4023233417, 2562383102, 271733878])
        },
        _doProcessBlock: function (t, e) {
            for (var a = 0; a < 16; a++) {
                var s = e + a
                    , u = t[s];
                t[s] = 16711935 & (u << 8 | u >>> 24) | 4278255360 & (u << 24 | u >>> 8)
            }
            var c = this._hash.words
                , l = t[e + 0]
                , d = t[e + 1]
                , h = t[e + 2]
                , p = t[e + 3]
                , m = t[e + 4]
                , y = t[e + 5]
                , _ = t[e + 6]
                , v = t[e + 7]
                , b = t[e + 8]
                , g = t[e + 9]
                , w = t[e + 10]
                , M = t[e + 11]
                , k = t[e + 12]
                , S = t[e + 13]
                , x = t[e + 14]
                , L = t[e + 15]
                , T = c[0]
                , D = c[1]
                , Y = c[2]
                , E = c[3];
            T = n(T, D, Y, E, l, 7, f[0]),
                E = n(E, T, D, Y, d, 12, f[1]),
                Y = n(Y, E, T, D, h, 17, f[2]),
                D = n(D, Y, E, T, p, 22, f[3]),
                T = n(T, D, Y, E, m, 7, f[4]),
                E = n(E, T, D, Y, y, 12, f[5]),
                Y = n(Y, E, T, D, _, 17, f[6]),
                D = n(D, Y, E, T, v, 22, f[7]),
                T = n(T, D, Y, E, b, 7, f[8]),
                E = n(E, T, D, Y, g, 12, f[9]),
                Y = n(Y, E, T, D, w, 17, f[10]),
                D = n(D, Y, E, T, M, 22, f[11]),
                T = n(T, D, Y, E, k, 7, f[12]),
                E = n(E, T, D, Y, S, 12, f[13]),
                Y = n(Y, E, T, D, x, 17, f[14]),
                D = n(D, Y, E, T, L, 22, f[15]),
                T = r(T, D, Y, E, d, 5, f[16]),
                E = r(E, T, D, Y, _, 9, f[17]),
                Y = r(Y, E, T, D, M, 14, f[18]),
                D = r(D, Y, E, T, l, 20, f[19]),
                T = r(T, D, Y, E, y, 5, f[20]),
                E = r(E, T, D, Y, w, 9, f[21]),
                Y = r(Y, E, T, D, L, 14, f[22]),
                D = r(D, Y, E, T, m, 20, f[23]),
                T = r(T, D, Y, E, g, 5, f[24]),
                E = r(E, T, D, Y, x, 9, f[25]),
                Y = r(Y, E, T, D, p, 14, f[26]),
                D = r(D, Y, E, T, b, 20, f[27]),
                T = r(T, D, Y, E, S, 5, f[28]),
                E = r(E, T, D, Y, h, 9, f[29]),
                Y = r(Y, E, T, D, v, 14, f[30]),
                D = r(D, Y, E, T, k, 20, f[31]),
                T = i(T, D, Y, E, y, 4, f[32]),
                E = i(E, T, D, Y, b, 11, f[33]),
                Y = i(Y, E, T, D, M, 16, f[34]),
                D = i(D, Y, E, T, x, 23, f[35]),
                T = i(T, D, Y, E, d, 4, f[36]),
                E = i(E, T, D, Y, m, 11, f[37]),
                Y = i(Y, E, T, D, v, 16, f[38]),
                D = i(D, Y, E, T, w, 23, f[39]),
                T = i(T, D, Y, E, S, 4, f[40]),
                E = i(E, T, D, Y, l, 11, f[41]),
                Y = i(Y, E, T, D, p, 16, f[42]),
                D = i(D, Y, E, T, _, 23, f[43]),
                T = i(T, D, Y, E, g, 4, f[44]),
                E = i(E, T, D, Y, k, 11, f[45]),
                Y = i(Y, E, T, D, L, 16, f[46]),
                D = i(D, Y, E, T, h, 23, f[47]),
                T = o(T, D, Y, E, l, 6, f[48]),
                E = o(E, T, D, Y, v, 10, f[49]),
                Y = o(Y, E, T, D, x, 15, f[50]),
                D = o(D, Y, E, T, y, 21, f[51]),
                T = o(T, D, Y, E, k, 6, f[52]),
                E = o(E, T, D, Y, p, 10, f[53]),
                Y = o(Y, E, T, D, w, 15, f[54]),
                D = o(D, Y, E, T, d, 21, f[55]),
                T = o(T, D, Y, E, b, 6, f[56]),
                E = o(E, T, D, Y, L, 10, f[57]),
                Y = o(Y, E, T, D, _, 15, f[58]),
                D = o(D, Y, E, T, S, 21, f[59]),
                T = o(T, D, Y, E, m, 6, f[60]),
                E = o(E, T, D, Y, M, 10, f[61]),
                Y = o(Y, E, T, D, h, 15, f[62]),
                D = o(D, Y, E, T, g, 21, f[63]),
                c[0] = c[0] + T | 0,
                c[1] = c[1] + D | 0,
                c[2] = c[2] + Y | 0,
                c[3] = c[3] + E | 0
        },
        _doFinalize: function () {
            var t = this._data
                , n = t.words
                , r = 8 * this._nDataBytes
                , i = 8 * t.sigBytes;
            n[i >>> 5] |= 128 << 24 - i % 32;
            var o = e.floor(r / 4294967296)
                , a = r;
            n[15 + (i + 64 >>> 9 << 4)] = 16711935 & (o << 8 | o >>> 24) | 4278255360 & (o << 24 | o >>> 8),
                n[14 + (i + 64 >>> 9 << 4)] = 16711935 & (a << 8 | a >>> 24) | 4278255360 & (a << 24 | a >>> 8),
                t.sigBytes = 4 * (n.length + 1),
                this._process();
            for (var s = this._hash, u = s.words, c = 0; c < 4; c++) {
                var l = u[c];
                u[c] = 16711935 & (l << 8 | l >>> 24) | 4278255360 & (l << 24 | l >>> 8)
            }
            return s
        },
        clone: function () {
            var t = c.clone.call(this);
            return t._hash = this._hash.clone(),
                t
        }
    });
    a.MD5 = c._createHelper(d),
        a.HmacMD5 = c._createHmacHelper(d)
})(Math);
(function () {
    var e = Myencrypter
        , n = e.lib
        , r = n.BlockCipher
        , i = e.algo
        , o = []
        , a = []
        , s = []
        , u = []
        , c = []
        , l = []
        , f = []
        , d = []
        , h = []
        , p = [];
    !function () {
        for (var t = [], e = 0; e < 256; e++)
            t[e] = e < 128 ? e << 1 : e << 1 ^ 283;
        for (var n = 0, r = 0, e = 0; e < 256; e++) {
            var i = r ^ r << 1 ^ r << 2 ^ r << 3 ^ r << 4;
            i = i >>> 8 ^ 255 & i ^ 99,
                o[n] = i,
                a[i] = n;
            var m = t[n]
                , y = t[m]
                , _ = t[y]
                , v = 257 * t[i] ^ 16843008 * i;
            s[n] = v << 24 | v >>> 8,
                u[n] = v << 16 | v >>> 16,
                c[n] = v << 8 | v >>> 24,
                l[n] = v;
            var v = 16843009 * _ ^ 65537 * y ^ 257 * m ^ 16843008 * n;
            f[i] = v << 24 | v >>> 8,
                d[i] = v << 16 | v >>> 16,
                h[i] = v << 8 | v >>> 24,
                p[i] = v,
                n ? (n = m ^ t[t[t[_ ^ m]]],
                    r ^= t[t[r]]) : n = r = 1
        }
    }();
    var m = [0, 1, 2, 4, 8, 16, 32, 64, 128, 27, 54]
        , y = i.AES = r.extend({
        _doReset: function () {
            if (!this._nRounds || this._keyPriorReset !== this._key) {
                for (var t = this._keyPriorReset = this._key, e = t.words, n = t.sigBytes / 4, r = this._nRounds = n + 6, i = 4 * (r + 1), a = this._keySchedule = [], s = 0; s < i; s++)
                    if (s < n)
                        a[s] = e[s];
                    else {
                        var u = a[s - 1];
                        s % n ? n > 6 && s % n == 4 && (u = o[u >>> 24] << 24 | o[u >>> 16 & 255] << 16 | o[u >>> 8 & 255] << 8 | o[255 & u]) : (u = u << 8 | u >>> 24,
                            u = o[u >>> 24] << 24 | o[u >>> 16 & 255] << 16 | o[u >>> 8 & 255] << 8 | o[255 & u],
                            u ^= m[s / n | 0] << 24),
                            a[s] = a[s - n] ^ u
                    }
                for (var c = this._invKeySchedule = [], l = 0; l < i; l++) {
                    var s = i - l;
                    if (l % 4)
                        var u = a[s];
                    else
                        var u = a[s - 4];
                    c[l] = l < 4 || s <= 4 ? u : f[o[u >>> 24]] ^ d[o[u >>> 16 & 255]] ^ h[o[u >>> 8 & 255]] ^ p[o[255 & u]]
                }
            }
        },
        encryptBlock: function (t, e) {
            this._doCryptBlock(t, e, this._keySchedule, s, u, c, l, o)
        },
        decryptBlock: function (t, e) {
            var n = t[e + 1];
            t[e + 1] = t[e + 3],
                t[e + 3] = n,
                this._doCryptBlock(t, e, this._invKeySchedule, f, d, h, p, a);
            var n = t[e + 1];
            t[e + 1] = t[e + 3],
                t[e + 3] = n
        },
        _doCryptBlock: function (t, e, n, r, i, o, a, s) {
            for (var u = this._nRounds, c = t[e] ^ n[0], l = t[e + 1] ^ n[1], f = t[e + 2] ^ n[2], d = t[e + 3] ^ n[3], h = 4, p = 1; p < u; p++) {
                var m = r[c >>> 24] ^ i[l >>> 16 & 255] ^ o[f >>> 8 & 255] ^ a[255 & d] ^ n[h++]
                    , y = r[l >>> 24] ^ i[f >>> 16 & 255] ^ o[d >>> 8 & 255] ^ a[255 & c] ^ n[h++]
                    , _ = r[f >>> 24] ^ i[d >>> 16 & 255] ^ o[c >>> 8 & 255] ^ a[255 & l] ^ n[h++]
                    , v = r[d >>> 24] ^ i[c >>> 16 & 255] ^ o[l >>> 8 & 255] ^ a[255 & f] ^ n[h++];
                c = m,
                    l = y,
                    f = _,
                    d = v
            }
            var m = (s[c >>> 24] << 24 | s[l >>> 16 & 255] << 16 | s[f >>> 8 & 255] << 8 | s[255 & d]) ^ n[h++]
                , y = (s[l >>> 24] << 24 | s[f >>> 16 & 255] << 16 | s[d >>> 8 & 255] << 8 | s[255 & c]) ^ n[h++]
                , _ = (s[f >>> 24] << 24 | s[d >>> 16 & 255] << 16 | s[c >>> 8 & 255] << 8 | s[255 & l]) ^ n[h++]
                , v = (s[d >>> 24] << 24 | s[c >>> 16 & 255] << 16 | s[l >>> 8 & 255] << 8 | s[255 & f]) ^ n[h++];
            t[e] = m,
                t[e + 1] = y,
                t[e + 2] = _,
                t[e + 3] = v
        },
        keySize: 8
    });
    e.AES = r._createHelper(y)
})();
(function () {
    var e = Myencrypter
        , n = e.lib
        , r = n.Base
        , i = n.WordArray
        , o = e.algo
        , a = o.MD5
        , s = o.EvpKDF = r.extend({
        cfg: r.extend({
            keySize: 4,
            hasher: a,
            iterations: 1
        }),
        init: function (t) {
            this.cfg = this.cfg.extend(t)
        },
        compute: function (t, e) {
            for (var n = this.cfg, r = n.hasher.create(), o = i.create(), a = o.words, s = n.keySize, u = n.iterations; a.length < s;) {
                c && r.update(c);
                var c = r.update(t).finalize(e);
                r.reset();
                for (var l = 1; l < u; l++)
                    c = r.finalize(c),
                        r.reset();
                o.concat(c)
            }
            return o.sigBytes = 4 * s,
                o
        }
    });
    e.EvpKDF = function (t, e, n) {
        return s.create(n).compute(t, e)
    }
})();
(function () {
    var n = Myencrypter
        , r = n.lib
        , i = r.Base
        , o = r.WordArray
        , a = n.x64 = {};
    a.Word = i.extend({
        init: function (t, e) {
            this.high = t,
                this.low = e
        }
    }),
        a.WordArray = i.extend({
            init: function (t, e) {
                t = this.words = t || [],
                    this.sigBytes = void 0 != e ? e : 8 * t.length
            },
            toX32: function () {
                for (var t = this.words, e = t.length, n = [], r = 0; r < e; r++) {
                    var i = t[r];
                    n.push(i.high),
                        n.push(i.low)
                }
                return o.create(n, this.sigBytes)
            },
            clone: function () {
                for (var t = i.clone.call(this), e = t.words = this.words.slice(0), n = e.length, r = 0; r < n; r++)
                    e[r] = e[r].clone();
                return t
            }
        })
})();
(function () {
    function e() {
        return a.create.apply(a, arguments)
    }

    var n = Myencrypter
        , r = n.lib
        , i = r.Hasher
        , o = n.x64
        , a = o.Word
        , s = o.WordArray
        , u = n.algo
        ,
        c = [e(1116352408, 3609767458), e(1899447441, 602891725), e(3049323471, 3964484399), e(3921009573, 2173295548), e(961987163, 4081628472), e(1508970993, 3053834265), e(2453635748, 2937671579), e(2870763221, 3664609560), e(3624381080, 2734883394), e(310598401, 1164996542), e(607225278, 1323610764), e(1426881987, 3590304994), e(1925078388, 4068182383), e(2162078206, 991336113), e(2614888103, 633803317), e(3248222580, 3479774868), e(3835390401, 2666613458), e(4022224774, 944711139), e(264347078, 2341262773), e(604807628, 2007800933), e(770255983, 1495990901), e(1249150122, 1856431235), e(1555081692, 3175218132), e(1996064986, 2198950837), e(2554220882, 3999719339), e(2821834349, 766784016), e(2952996808, 2566594879), e(3210313671, 3203337956), e(3336571891, 1034457026), e(3584528711, 2466948901), e(113926993, 3758326383), e(338241895, 168717936), e(666307205, 1188179964), e(773529912, 1546045734), e(1294757372, 1522805485), e(1396182291, 2643833823), e(1695183700, 2343527390), e(1986661051, 1014477480), e(2177026350, 1206759142), e(2456956037, 344077627), e(2730485921, 1290863460), e(2820302411, 3158454273), e(3259730800, 3505952657), e(3345764771, 106217008), e(3516065817, 3606008344), e(3600352804, 1432725776), e(4094571909, 1467031594), e(275423344, 851169720), e(430227734, 3100823752), e(506948616, 1363258195), e(659060556, 3750685593), e(883997877, 3785050280), e(958139571, 3318307427), e(1322822218, 3812723403), e(1537002063, 2003034995), e(1747873779, 3602036899), e(1955562222, 1575990012), e(2024104815, 1125592928), e(2227730452, 2716904306), e(2361852424, 442776044), e(2428436474, 593698344), e(2756734187, 3733110249), e(3204031479, 2999351573), e(3329325298, 3815920427), e(3391569614, 3928383900), e(3515267271, 566280711), e(3940187606, 3454069534), e(4118630271, 4000239992), e(116418474, 1914138554), e(174292421, 2731055270), e(289380356, 3203993006), e(460393269, 320620315), e(685471733, 587496836), e(852142971, 1086792851), e(1017036298, 365543100), e(1126000580, 2618297676), e(1288033470, 3409855158), e(1501505948, 4234509866), e(1607167915, 987167468), e(1816402316, 1246189591)]
        , l = [];
    !function () {
        for (var t = 0; t < 80; t++)
            l[t] = e()
    }();
    var f = u.SHA512 = i.extend({
        _doReset: function () {
            this._hash = new s.init([new a.init(1779033703, 4089235720), new a.init(3144134277, 2227873595), new a.init(1013904242, 4271175723), new a.init(2773480762, 1595750129), new a.init(1359893119, 2917565137), new a.init(2600822924, 725511199), new a.init(528734635, 4215389547), new a.init(1541459225, 327033209)])
        },
        _doProcessBlock: function (t, e) {
            for (var n = this._hash.words, r = n[0], i = n[1], o = n[2], a = n[3], s = n[4], u = n[5], f = n[6], d = n[7], h = r.high, p = r.low, m = i.high, y = i.low, _ = o.high, v = o.low, b = a.high, g = a.low, w = s.high, M = s.low, k = u.high, S = u.low, x = f.high, L = f.low, T = d.high, D = d.low, Y = h, E = p, j = m, C = y, A = _, P = v, O = b, I = g, H = w, N = M, R = k, B = S, F = x, z = L, q = T, W = D, U = 0; U < 80; U++) {
                var $ = l[U];
                if (U < 16)
                    var V = $.high = 0 | t[e + 2 * U]
                        , K = $.low = 0 | t[e + 2 * U + 1];
                else {
                    var J = l[U - 15]
                        , G = J.high
                        , X = J.low
                        , Q = (G >>> 1 | X << 31) ^ (G >>> 8 | X << 24) ^ G >>> 7
                        , Z = (X >>> 1 | G << 31) ^ (X >>> 8 | G << 24) ^ (X >>> 7 | G << 25)
                        , tt = l[U - 2]
                        , et = tt.high
                        , nt = tt.low
                        , rt = (et >>> 19 | nt << 13) ^ (et << 3 | nt >>> 29) ^ et >>> 6
                        , it = (nt >>> 19 | et << 13) ^ (nt << 3 | et >>> 29) ^ (nt >>> 6 | et << 26)
                        , ot = l[U - 7]
                        , at = ot.high
                        , st = ot.low
                        , ut = l[U - 16]
                        , ct = ut.high
                        , lt = ut.low
                        , K = Z + st
                        , V = Q + at + (K >>> 0 < Z >>> 0 ? 1 : 0)
                        , K = K + it
                        , V = V + rt + (K >>> 0 < it >>> 0 ? 1 : 0)
                        , K = K + lt
                        , V = V + ct + (K >>> 0 < lt >>> 0 ? 1 : 0);
                    $.high = V,
                        $.low = K
                }
                var ft = H & R ^ ~H & F
                    , dt = N & B ^ ~N & z
                    , ht = Y & j ^ Y & A ^ j & A
                    , pt = E & C ^ E & P ^ C & P
                    , mt = (Y >>> 28 | E << 4) ^ (Y << 30 | E >>> 2) ^ (Y << 25 | E >>> 7)
                    , yt = (E >>> 28 | Y << 4) ^ (E << 30 | Y >>> 2) ^ (E << 25 | Y >>> 7)
                    , _t = (H >>> 14 | N << 18) ^ (H >>> 18 | N << 14) ^ (H << 23 | N >>> 9)
                    , vt = (N >>> 14 | H << 18) ^ (N >>> 18 | H << 14) ^ (N << 23 | H >>> 9)
                    , bt = c[U]
                    , gt = bt.high
                    , wt = bt.low
                    , Mt = W + vt
                    , kt = q + _t + (Mt >>> 0 < W >>> 0 ? 1 : 0)
                    , Mt = Mt + dt
                    , kt = kt + ft + (Mt >>> 0 < dt >>> 0 ? 1 : 0)
                    , Mt = Mt + wt
                    , kt = kt + gt + (Mt >>> 0 < wt >>> 0 ? 1 : 0)
                    , Mt = Mt + K
                    , kt = kt + V + (Mt >>> 0 < K >>> 0 ? 1 : 0)
                    , St = yt + pt
                    , xt = mt + ht + (St >>> 0 < yt >>> 0 ? 1 : 0);
                q = F,
                    W = z,
                    F = R,
                    z = B,
                    R = H,
                    B = N,
                    N = I + Mt | 0,
                    H = O + kt + (N >>> 0 < I >>> 0 ? 1 : 0) | 0,
                    O = A,
                    I = P,
                    A = j,
                    P = C,
                    j = Y,
                    C = E,
                    E = Mt + St | 0,
                    Y = kt + xt + (E >>> 0 < Mt >>> 0 ? 1 : 0) | 0
            }
            p = r.low = p + E,
                r.high = h + Y + (p >>> 0 < E >>> 0 ? 1 : 0),
                y = i.low = y + C,
                i.high = m + j + (y >>> 0 < C >>> 0 ? 1 : 0),
                v = o.low = v + P,
                o.high = _ + A + (v >>> 0 < P >>> 0 ? 1 : 0),
                g = a.low = g + I,
                a.high = b + O + (g >>> 0 < I >>> 0 ? 1 : 0),
                M = s.low = M + N,
                s.high = w + H + (M >>> 0 < N >>> 0 ? 1 : 0),
                S = u.low = S + B,
                u.high = k + R + (S >>> 0 < B >>> 0 ? 1 : 0),
                L = f.low = L + z,
                f.high = x + F + (L >>> 0 < z >>> 0 ? 1 : 0),
                D = d.low = D + W,
                d.high = T + q + (D >>> 0 < W >>> 0 ? 1 : 0)
        },
        _doFinalize: function () {
            var t = this._data
                , e = t.words
                , n = 8 * this._nDataBytes
                , r = 8 * t.sigBytes;
            return e[r >>> 5] |= 128 << 24 - r % 32,
                e[30 + (r + 128 >>> 10 << 5)] = Math.floor(n / 4294967296),
                e[31 + (r + 128 >>> 10 << 5)] = n,
                t.sigBytes = 4 * e.length,
                this._process(),
                this._hash.toX32()
        },
        clone: function () {
            var t = i.clone.call(this);
            return t._hash = this._hash.clone(),
                t
        },
        blockSize: 32
    });
    n.SHA512 = i._createHelper(f),
        n.HmacSHA512 = i._createHmacHelper(f)
})();
(function () {
    var e = Myencrypter
        , n = e.lib
        , r = n.Base
        , i = e.enc
        , o = i.Utf8
        , a = e.algo;
    a.HMAC = r.extend({
        init: function (t, e) {
            t = this._hasher = new t.init,
            "string" == typeof e && (e = o.parse(e));
            var n = t.blockSize
                , r = 4 * n;
            e.sigBytes > r && (e = t.finalize(e)),
                e.clamp();
            for (var i = this._oKey = e.clone(), a = this._iKey = e.clone(), s = i.words, u = a.words, c = 0; c < n; c++)
                s[c] ^= 1549556828,
                    u[c] ^= 909522486;
            i.sigBytes = a.sigBytes = r,
                this.reset()
        },
        reset: function () {
            var t = this._hasher;
            t.reset(),
                t.update(this._iKey)
        },
        update: function (t) {
            return this._hasher.update(t),
                this
        },
        finalize: function (t) {
            var e = this._hasher
                , n = e.finalize(t);
            return e.reset(),
                e.finalize(this._oKey.clone().concat(n))
        }
    })
})();

function encrypt(password) {
    return Myencrypter.AES.encrypt(password, "123456781bcddfkpwefkoeprgpjgpte").toString()
}

function o_HmacMd5(t, e) {
    return (0, Myencrypter.HmacMD5)(t, e).toString()
}

function o_HmacSHA1(t, e) {
    return (0, Myencrypter.HmacSHA1)(t, e).toString()
}

function o_HmacSHA512(t, e) {
    return (0, Myencrypter.HmacSHA512)(t, e).toString()
}

function s_default(codes, params) {
    for (var t = params, e = t.toLowerCase(), n = e + e, r = "", o = 0; o < n.length; ++o) {
        var a = n[o].charCodeAt() % 20;
        r += codes[a]
    }
    return r
}
function header_key(codes, url) {
    var t = url.replace("https://www.qixin.com", "")
        , e = t.toLowerCase();
    return (0,
        o_HmacSHA512)(e, (0,
        s_default)(codes, e)).toLowerCase().substr(10, 20)
}
function header_value(codes, url, data) {
    var t = url.replace("https://www.qixin.com", "")
        , n = t.toLowerCase()
        , r = JSON.stringify(data).toLowerCase();
    return (0,
        o_HmacSHA512)(n + n + r, (0,
        s_default)(codes, n))
}
// var codes = {
//     0: "2",
//     1: "t",
//     2: "W",
//     3: "Y",
//     4: "E",
//     5: "Q",
//     6: "P",
//     7: "v",
//     8: "k",
//     9: "l",
//     10: "X",
//     11: "z",
//     12: "K",
//     13: "W",
//     14: "r",
//     15: "L",
//     16: "g",
//     17: "v",
//     18: "Z",
//     19: "J",
// };
// console.log(header_key(codes, 'https://www.qixin.com/api/search/searchBrand'));
// console.log(header_value(codes, 'https://www.qixin.com/api/search/searchBrand', {"keyword": "网易", "start": 20, "hit": 10}));
