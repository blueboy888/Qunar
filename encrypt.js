var MyEncrypter = {};  // 该代码已删除, 请自行补全
function a(e) {
    return e && e.__esModule ? e : {
        "default": e
    }
}
function f(e, t) {
    if (!(e instanceof t)) {
        throw new TypeError("Cannot call a class as a function")
    }
}
var r = function() {
    function e(e, t) {
        for (var n = 0; n < t.length; n++) {
            var r = t[n];
            r.enumerable = r.enumerable || false;
            r.configurable = true;
            if ("value" in r)
                r.writable = true;
            Object.defineProperty(e, r.key, r)
        }
    }
    return function (t, n, r) {
        if (n)
            e(t.prototype, n);
        if (r)
            e(t, r);
        return t
    }
}();
var l = function() {
    function e() {
        f(this, e);
        this.qtTime = [83, 80, 56, 56, 58];
        this.cookieToken = [83, 80, 54, 58];
        this.tokenStr = [115, 119, 112, 99, 116, 97, 99, 114, 107, 97, 118, 113, 109, 103, 112]
    }
    r(e, [{
        key: "getCookie",
        value: function (t) {
            var n = cookie.split("; ");
            for (var r = 0; r < n.length; r++) {
                var i = n[r].split("=");
                if (i[0] === t) {
                    return decodeURIComponent(i[1])
                }
            }
            return null
        }
    }, {
        key: "getRandomKey",
        value: function (t) {
            var n = "";
            var r = ("" + t).substr(4);
            r.split("").forEach(function (e) {
                n += e.charCodeAt()
            });
            var i = (0, MyEncrypter.MD5)(n).toString();
            return i.substr(-6)
        }
    }, {
        key: "getToken",
        value: function () {
            var t = {};
            t[this.getRandomKey(this.getQtTime(this.getCookie(this.dencryptCode(this.qtTime))))] = this.encrypt();
            return t
        }
    }, {
        key: "encryptFunction",
        value: function () {
            return [function (e) {
                var t = (0, MyEncrypter.SHA1)(e).toString();
                return (0, MyEncrypter.MD5)(t).toString();
            }
            , function (e) {
                    var t = (0, MyEncrypter.SHA1)(e).toString();
                    return (0, MyEncrypter.MD5)(t).toString();
                }
            ]
        }
    }, {
        key: "dencryptCode",
        value: function (t) {
            return t.map(function (e) {
                return String.fromCharCode(e - 2)
            }).join("")
        }
    }, {
        key: "getQtTime",
        value: function (t) {
            return t ? Number(t.split(",").map(function (e) {
                return String.fromCharCode(e - 2)
            }).join("")) : 0
        }
    }, {
        key: "getTokenStr",
        value: function () {
            var t = this.dencryptCode(this.tokenStr);
            // var n = document.getElementById(t);
            // var r = n && n.innerHTML;
            var r = null;
            return r ? r : this.getCookie(this.dencryptCode(this.cookieToken))
        }
    }, {
        key: "encrypt",
        value: function () {
            var t = this.getTokenStr()
              , n = this.getQtTime(this.getCookie(this.dencryptCode(this.qtTime)))
              , r = n % 2;
            return this.encryptFunction()[r](t + n)
        }
    }]);
    return e
}();

function get__m__(cookies) {
    cookie = cookies;
    h = new l ();
    return {
        header: h.getToken(),
        __m__: (0, MyEncrypter.MD5)(h.encrypt()).toString()
    }
}
