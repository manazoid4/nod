package uk.mazworks.piblo.proto

import org.json.JSONArray
import org.json.JSONObject

/** piblo-proto v1 = the existing Core buddy HTTP+JSON routes. Pure Kotlin (org.json only) so it unit-tests on the JVM. */

const val TITLE_MAX = 60      // docs/ALERTS.md
const val BODY_MAX = 200      // docs/ALERTS.md
const val SOURCE_MAX = 40     // AlertIn.source
const val KIND_FIND_PHONE = "find_phone"

enum class Priority(val wire: String) {
    LOW("low"), NORMAL("normal"), HIGH("high"), URGENT("urgent");
    companion object { fun parse(s: String?) = entries.firstOrNull { it.wire == s } ?: NORMAL }
}

data class PendingApproval(val id: String, val tool: String, val summary: String, val project: String, val leftSeconds: Int)

data class AlertMsg(
    val id: String, val source: String, val kind: String, val title: String, val body: String,
    val priority: Priority, val actions: List<String>,
) {
    /** Additive kind from the Android lane. Until Core accepts it, `source: "find_phone"` is the interim wire form. */
    val isFindPhone get() = kind == KIND_FIND_PHONE || source == KIND_FIND_PHONE
}

data class CoreEvent(val id: Int, val kind: String, val text: String, val source: String, val alert: AlertMsg?)
data class Summary(val agent: String, val count: Int, val items: List<PendingApproval>)
data class EventsPage(val events: List<CoreEvent>, val last: Int)

class ProtoException(message: String) : Exception(message)

object Proto {
    fun parseSummary(json: String): Summary = guard {
        val o = JSONObject(json)
        val items = o.optJSONArray("items") ?: JSONArray()
        Summary(
            o.optString("agent", "idle"), o.optInt("count", items.length()),
            (0 until items.length()).mapNotNull { i ->
                val it = items.optJSONObject(i) ?: return@mapNotNull null
                val id = it.optString("id")
                if (id.isEmpty()) null
                else PendingApproval(id, it.optString("tool"), it.optString("summary"), it.optString("project"), it.optInt("left", 0))
            },
        )
    }

    fun parseEvents(json: String): EventsPage = guard {
        val o = JSONObject(json)
        val arr = o.optJSONArray("events") ?: JSONArray()
        EventsPage(
            (0 until arr.length()).mapNotNull { i ->
                val e = arr.optJSONObject(i) ?: return@mapNotNull null
                // Unknown kinds are kept (old/new peers must ignore, not crash): the caller decides what to show.
                CoreEvent(e.optInt("id", -1), e.optString("kind"), e.optString("text"), e.optString("source"), e.optJSONObject("alert")?.let(::parseAlert))
            },
            o.optInt("last", 0),
        )
    }

    private fun parseAlert(a: JSONObject): AlertMsg {
        val acts = a.optJSONArray("actions")
        return AlertMsg(
            a.optString("id"), a.optString("source"), a.optString("kind", "info"), a.optString("title"), a.optString("body"),
            Priority.parse(a.optString("priority")), if (acts == null) listOf("ack") else (0 until acts.length()).map { acts.optString(it) },
        )
    }

    /** FastAPI errors look like {"detail":"authentication_required"}; 422 has a list, so flatten defensively. */
    fun parseError(body: String): String = try {
        val d = JSONObject(body).opt("detail")
        if (d is String) d else "bad_request"
    } catch (_: Exception) { "" }

    fun parseToken(json: String): String = guard { JSONObject(json).getString("token") }

    fun parsePostedId(json: String): String = guard { JSONObject(json).getString("id") }

    /** Truncates by code point (Core counts Python characters), never splitting a surrogate pair. */
    fun truncate(s: String, max: Int): String {
        val t = s.trim()
        return if (t.codePointCount(0, t.length) <= max) t else t.substring(0, t.offsetByCodePoints(0, max))
    }

    fun alertJson(source: String, kind: String, title: String, body: String, priority: Priority, actions: List<String> = listOf("ack")): String =
        JSONObject()
            .put("source", truncate(source, SOURCE_MAX).ifEmpty { "phone" })
            .put("kind", kind)
            .put("title", truncate(title, TITLE_MAX).ifEmpty { "(no title)" })
            .put("body", truncate(body, BODY_MAX))
            .put("priority", priority.wire)
            .put("actions", JSONArray(actions))
            .toString()

    fun decideJson(id: String, allow: Boolean): String = JSONObject().put("id", id).put("decision", if (allow) "allow" else "deny").toString()

    private inline fun <T> guard(block: () -> T): T = try { block() } catch (e: ProtoException) { throw e } catch (e: Exception) { throw ProtoException("unexpected response: ${e.message}") }
}
