package uk.mazworks.piblo.hub

import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import uk.mazworks.piblo.proto.AlertMsg
import uk.mazworks.piblo.proto.EventsPage
import uk.mazworks.piblo.proto.Priority
import uk.mazworks.piblo.proto.Summary

/** What the (simulated) Piblo screen is asked to show right now, and what the person answered. No Android types: JVM-testable. */

const val APPROVAL_TIMEOUT_MS = 60_000L   // same window as Core (buddy.TIMEOUT_S)
const val MAX_QUEUE = 20
const val MAX_ACTIVITY = 50
const val MAX_OUTBOX = 20
const val SNOOZE_MIN = 10

enum class ItemKind { APPROVAL, ALERT }
enum class Origin { LOCAL, CORE }
enum class LinkState { SIMULATOR, CONNECTING, ONLINE, OFFLINE, AUTH_FAILED }
enum class Answer { APPROVE, REJECT, SNOOZE, ACK }

data class Item(
    val id: String, val kind: ItemKind, val title: String, val body: String, val priority: Priority,
    val actions: List<String>, val origin: Origin, val deadlineMs: Long? = null, val alertKind: String = "info",
) {
    val canSnooze get() = kind == ItemKind.ALERT && "snooze" in actions
}

data class Activity(val atWallMs: Long, val text: String)

data class HubState(
    val queue: List<Item> = emptyList(),
    val activity: List<Activity> = emptyList(),
    val link: LinkState = LinkState.SIMULATOR,
    val agent: String = "idle",
    val ringing: Boolean = false,
) { val head: Item? get() = queue.firstOrNull() }

sealed interface Outgoing {
    data class Decide(val id: String, val allow: Boolean, val deadlineMs: Long) : Outgoing
    data class AlertAction(val id: String, val action: String, val minutes: Int = SNOOZE_MIN, val tries: Int = 0) : Outgoing
}

interface Clock { fun mono(): Long; fun wall(): Long }

/** Side effects live behind this so the Hub stays pure. */
interface HubEvents {
    fun shown(item: Item, source: String) {}      // new item reached the screen (notify + save to Messages)
    fun findPhone() {}
}

class Hub(private val clock: Clock, private val events: HubEvents) {
    private val s = MutableStateFlow(HubState())
    val state: StateFlow<HubState> = s
    private val outbox = ArrayDeque<Outgoing>()
    private val snoozed = ArrayList<Pair<Long, Item>>()
    private var simCounter = 0

    // ---- local (simulator / reminders / forwarded notifications) ----
    @Synchronized fun localApproval(tool: String, summary: String): String {
        val id = "sim-${++simCounter}"
        show(Item(id, ItemKind.APPROVAL, tool, summary, Priority.URGENT, listOf("approve", "reject"), Origin.LOCAL, clock.mono() + APPROVAL_TIMEOUT_MS), "simulator")
        return id
    }

    @Synchronized fun localAlert(title: String, body: String, priority: Priority = Priority.NORMAL, kind: String = "info", source: String = "phone") {
        show(Item("loc-${++simCounter}", ItemKind.ALERT, title, body, priority, listOf("ack", "snooze"), Origin.LOCAL, null, kind), source)
    }

    @Synchronized fun setRinging(on: Boolean) { s.value = s.value.copy(ringing = on) }

    // ---- answers from the buttons ----
    @Synchronized fun answer(a: Answer) {
        val item = s.value.head ?: return
        when {
            item.kind == ItemKind.APPROVAL && (a == Answer.APPROVE || a == Answer.REJECT) -> {
                val allow = a == Answer.APPROVE
                if (item.origin == Origin.CORE) queue(Outgoing.Decide(item.id, allow, item.deadlineMs ?: (clock.mono() + APPROVAL_TIMEOUT_MS)))
                log("${if (allow) "Approved" else "Rejected"}: ${item.title}")
                remove(item.id)
            }
            item.kind == ItemKind.ALERT && a == Answer.SNOOZE && item.canSnooze -> {
                if (item.origin == Origin.CORE) queue(Outgoing.AlertAction(item.id, "snooze"))
                else snoozed += clock.mono() + SNOOZE_MIN * 60_000L to item
                log("Snoozed ${SNOOZE_MIN} min: ${item.title}")
                remove(item.id)
            }
            item.kind == ItemKind.ALERT && a == Answer.ACK -> {
                if (item.origin == Origin.CORE) queue(Outgoing.AlertAction(item.id, "ack"))
                log("Done: ${item.title}")
                remove(item.id)
            }
        }
    }

    // ---- housekeeping: call about once a second ----
    @Synchronized fun tick() {
        val now = clock.mono()
        // Fail closed: an approval nobody answered in time is gone; Core denies it on its own timeout.
        s.value.queue.filter { it.kind == ItemKind.APPROVAL && it.deadlineMs != null && now >= it.deadlineMs }.forEach {
            log("Timed out, not approved: ${it.title}"); remove(it.id)
        }
        outbox.removeAll { it is Outgoing.Decide && now >= it.deadlineMs }
        val due = snoozed.filter { now >= it.first }
        if (due.isNotEmpty()) { snoozed.removeAll(due.toSet()); due.forEach { show(it.second, "reminder") } }
    }

    // ---- from the computer link ----
    @Synchronized fun setLink(l: LinkState) { if (s.value.link != l) s.value = s.value.copy(link = l) }

    @Synchronized fun applyPoll(summary: Summary, page: EventsPage, initial: Boolean) {
        val now = clock.mono()
        val live = summary.items.map { it.id }.toSet()
        // An approval that left Core's pending list (decided at the computer, or expired) must leave the screen too.
        s.value.queue.filter { it.origin == Origin.CORE && it.kind == ItemKind.APPROVAL && it.id !in live }.forEach { remove(it.id) }
        summary.items.forEach { a ->
            if (s.value.queue.none { it.id == a.id } && a.leftSeconds > 0)
                show(Item(a.id, ItemKind.APPROVAL, a.tool.ifBlank { "Approval" }, a.summary, Priority.URGENT, listOf("approve", "reject"), Origin.CORE, now + a.leftSeconds * 1000L), a.project.ifBlank { "computer" })
        }
        s.value = s.value.copy(agent = summary.agent)
        if (initial) return   // start from "now": old ring entries are not replayed as fresh alerts or alarms
        page.events.forEach { e ->
            val al = e.alert
            when {
                al != null && al.isFindPhone -> { queue(Outgoing.AlertAction(al.id, "ack")); log("Find my phone from ${al.source}"); events.findPhone() }
                al != null -> showAlert(al)
                e.kind in setOf("done", "needs", "error", "usage") -> log("${e.source.ifBlank { "computer" }}: ${e.kind}${if (e.text.isBlank()) "" else " - " + e.text}")
            }
        }
    }

    private fun showAlert(a: AlertMsg) {
        if (s.value.queue.any { it.id == a.id }) return
        show(Item(a.id, ItemKind.ALERT, a.title, a.body, a.priority, a.actions, Origin.CORE, null, a.kind), a.source)
    }

    /** Outbox is drained by the link; a failed item goes back unless it is spent. */
    @Synchronized fun nextOutgoing(): Outgoing? = outbox.firstOrNull()
    @Synchronized fun sent(o: Outgoing) { outbox.remove(o) }
    @Synchronized fun failed(o: Outgoing, giveUp: Boolean) {
        outbox.remove(o)
        if (giveUp) { log("Could not tell the computer (${if (o is Outgoing.Decide) "decision" else "alert answer"})"); return }
        if (o is Outgoing.AlertAction) { if (o.tries < 2) outbox.addFirst(o.copy(tries = o.tries + 1)) else log("Gave up answering an alert") }
        else outbox.addFirst(o)   // a Decide is retried until its own deadline (tick() drops it)
    }
    @Synchronized fun outboxSize() = outbox.size

    // ---- internals ----
    fun log(text: String) {
        val list = listOf(Activity(clock.wall(), text)) + s.value.activity
        s.value = s.value.copy(activity = list.take(MAX_ACTIVITY))
    }

    private fun queue(o: Outgoing) {
        if (outbox.size >= MAX_OUTBOX) outbox.removeFirst()
        outbox.addLast(o)
    }

    private fun show(item: Item, source: String) {
        if (s.value.queue.any { it.id == item.id }) return
        var q = s.value.queue + item
        if (q.size > MAX_QUEUE) {   // drop the oldest alert first; approvals are the last thing to lose
            val drop = q.firstOrNull { it.kind == ItemKind.ALERT } ?: q.first()
            q = q - drop
        }
        s.value = s.value.copy(queue = q.sortedWith(compareBy<Item> { it.kind != ItemKind.APPROVAL }.thenByDescending { it.priority.ordinal }.thenBy { it.deadlineMs ?: Long.MAX_VALUE }))
        events.shown(item, source)
    }

    private fun remove(id: String) {
        s.value = s.value.copy(queue = s.value.queue.filter { it.id != id })
    }
}
