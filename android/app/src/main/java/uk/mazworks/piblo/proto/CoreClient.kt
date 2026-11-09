package uk.mazworks.piblo.proto

import java.io.IOException
import java.net.HttpURLConnection
import java.net.URL

/** HTTP status + Core's `detail` string (e.g. 401 authentication_required, 409 approval_expired). */
class CoreHttpException(val status: Int, val detail: String) : IOException("HTTP $status $detail")

/** Blocking client for the routes the firmware uses. Call from Dispatchers.IO. */
class CoreClient(baseUrl: String, private val token: String, private val clientVersion: String) {
    private val base = baseUrl.trimEnd('/')

    fun summary(): Summary = Proto.parseSummary(call("GET", "/buddy/summary"))
    fun events(since: Int): EventsPage = Proto.parseEvents(call("GET", "/buddy/events?since=$since"))
    fun decide(id: String, allow: Boolean) { call("POST", "/buddy/decide", Proto.decideJson(id, allow)) }
    fun alertAction(id: String, action: String, minutes: Int = 10) {
        require(action == "ack" || action == "snooze")
        call("POST", "/buddy/alert/${java.net.URLEncoder.encode(id, "UTF-8")}/$action", if (action == "snooze") """{"minutes":$minutes}""" else "{}")
    }
    fun postAlert(json: String): String = Proto.parsePostedId(call("POST", "/buddy/alert", json))

    /** Phone keyboard mode: send literal text to the focused Piblo field. Returns the record id. */
    fun postText(id: String, text: String, mode: String): String = Proto.parseTextId(call("POST", "/buddy/text", Proto.textJson(id, text, mode)))

    /** The device's answer for a text send: pending / inserted / no_field / too_long. */
    fun textStatus(id: String): String = Proto.parseTextStatus(call("GET", "/buddy/text/${java.net.URLEncoder.encode(id, "UTF-8")}"))

    private fun call(method: String, path: String, body: String? = null): String = request(base, method, path, body, token, clientVersion)

    companion object {
        const val DEFAULT_PORT = 8787
        private const val MAX_BODY = 64 * 1024

        /** "192.168.1.20" / "pc:8787" / "http://pc:8787/" -> "http://host:port". Returns null if it is not a usable address. */
        fun normalizeBase(input: String): String? {
            var s = input.trim().trimEnd('/')
            if (s.isEmpty() || s.any { it.isWhitespace() }) return null
            if (!s.contains("://")) s = "http://$s"
            val u = try { URL(s) } catch (_: Exception) { return null }
            if (u.protocol != "http" && u.protocol != "https") return null
            if (u.host.isNullOrEmpty()) return null
            val port = if (u.port == -1 && u.protocol == "http") ":$DEFAULT_PORT" else if (u.port == -1) "" else ":${u.port}"
            return "${u.protocol}://${u.host}$port"
        }

        /** Pairing: the code shown by Core is single-use; the reply is the token (stored encrypted by the caller). */
        fun claim(baseUrl: String, code: String, clientVersion: String): String =
            Proto.parseToken(request(baseUrl.trimEnd('/'), "POST", "/pair/claim", """{"code":"${code.trim().uppercase().filter { it.isLetterOrDigit() }}"}""", null, clientVersion))

        private fun readCapped(s: java.io.InputStream): String {
            val out = java.io.ByteArrayOutputStream()
            val buf = ByteArray(4096)
            while (out.size() < MAX_BODY) {
                val n = s.read(buf)
                if (n < 0) break
                out.write(buf, 0, n)
            }
            return out.toString("UTF-8")
        }

        internal fun request(base: String, method: String, path: String, body: String?, token: String?, clientVersion: String): String {
            val c = URL(base + path).openConnection() as HttpURLConnection
            try {
                c.requestMethod = method
                c.connectTimeout = 4000
                c.readTimeout = 8000
                c.instanceFollowRedirects = false
                c.setRequestProperty("X-Piblo-Client", "android/$clientVersion")
                c.setRequestProperty("Accept", "application/json")
                if (token != null) c.setRequestProperty("Authorization", "Bearer $token")
                if (body != null) {
                    c.doOutput = true
                    c.setRequestProperty("Content-Type", "application/json")
                    c.outputStream.use { it.write(body.toByteArray(Charsets.UTF_8)) }
                }
                val status = c.responseCode
                val stream = if (status in 200..299) c.inputStream else c.errorStream
                val text = stream?.use { readCapped(it) } ?: ""
                if (status !in 200..299) throw CoreHttpException(status, Proto.parseError(text))
                return text
            } finally { c.disconnect() }
        }
    }
}
