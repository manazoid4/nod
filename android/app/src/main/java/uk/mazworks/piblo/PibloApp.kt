package uk.mazworks.piblo

import android.app.Activity
import android.app.Application
import android.os.Bundle
import android.os.SystemClock
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.collectLatest
import kotlinx.coroutines.flow.distinctUntilChanged
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch
import uk.mazworks.piblo.data.Message
import uk.mazworks.piblo.data.Prefs
import uk.mazworks.piblo.data.PibloDb
import uk.mazworks.piblo.data.SecretBox
import uk.mazworks.piblo.data.SettingsRepo
import uk.mazworks.piblo.hub.Clock
import uk.mazworks.piblo.hub.CoreLink
import uk.mazworks.piblo.hub.CoreTransport
import uk.mazworks.piblo.hub.Hub
import uk.mazworks.piblo.hub.HubEvents
import uk.mazworks.piblo.hub.Item
import uk.mazworks.piblo.hub.ItemKind
import uk.mazworks.piblo.hub.LinkState
import uk.mazworks.piblo.hub.Origin
import uk.mazworks.piblo.hub.Transport
import uk.mazworks.piblo.proto.CoreClient
import uk.mazworks.piblo.proto.Priority
import uk.mazworks.piblo.proto.Proto
import uk.mazworks.piblo.system.FindPhone
import uk.mazworks.piblo.system.Notifier
import uk.mazworks.piblo.system.WatchService

class PibloApp : Application() {
    val scope = CoroutineScope(SupervisorJob() + Dispatchers.Default)
    val db by lazy { PibloDb.get(this) }
    val settings by lazy { SettingsRepo(this) }
    @Volatile private var visible = 0
    @Volatile private var transport: Transport? = null
    private var linkJob: Job? = null
    private var lastForward = 0L
    private var lastForwardKey = ""

    val hub = Hub(
        object : Clock {
            override fun mono() = SystemClock.elapsedRealtime()
            override fun wall() = System.currentTimeMillis()
        },
        object : HubEvents {
            override fun shown(item: Item, source: String) = this@PibloApp.onShown(item, source)
            override fun findPhone() = FindPhone.start(this@PibloApp)
        },
    )

    override fun onCreate() {
        super.onCreate()
        inst = this
        Notifier.channels(this)
        registerActivityLifecycleCallbacks(object : ActivityLifecycleCallbacks {
            override fun onActivityStarted(a: Activity) { visible++ }
            override fun onActivityStopped(a: Activity) { visible-- }
            override fun onActivityCreated(a: Activity, b: Bundle?) {}
            override fun onActivityResumed(a: Activity) {}
            override fun onActivityPaused(a: Activity) {}
            override fun onActivitySaveInstanceState(a: Activity, b: Bundle) {}
            override fun onActivityDestroyed(a: Activity) {}
        })
        scope.launch { while (isActive) { delay(1000); hub.tick() } }
        scope.launch {
            settings.prefs.map { it.copy(forwardNotifications = false, forwardPackages = emptySet()) }.distinctUntilChanged().collectLatest(::applyMode)
        }
    }

    /** Starts or stops the computer link when the connection settings change. */
    private fun applyMode(p: Prefs) {
        linkJob?.cancel()
        transport = null
        WatchService.set(this, p.mode == Prefs.Mode.COMPUTER && p.hasComputer && p.watchInBackground)
        if (p.mode != Prefs.Mode.COMPUTER || !p.hasComputer) { hub.setLink(LinkState.SIMULATOR); return }
        val token = SecretBox.decrypt(p.tokenBlob)
        if (token == null) { hub.setLink(LinkState.AUTH_FAILED); hub.log("Saved pairing can't be read. Connect again."); return }
        val t = CoreTransport(CoreClient(p.coreUrl, token, BuildConfig.VERSION_NAME))
        transport = t
        hub.setLink(LinkState.CONNECTING)
        val link = CoreLink(hub, t)
        linkJob = scope.launch(Dispatchers.IO) { while (isActive) delay(link.cycle()) }
    }

    private fun onShown(item: Item, source: String) {
        scope.launch(Dispatchers.IO) {
            val dao = db.dao()
            dao.insert(Message(atMs = System.currentTimeMillis(), source = source, title = item.title, body = item.body, priority = item.priority.wire))
            dao.trimMessages()
        }
        // Notify only for things the person has to act on, and only when the app is closed. Forwarded phone notifications are not repeated.
        if (visible <= 0 && (item.kind == ItemKind.APPROVAL || item.origin == Origin.CORE || item.alertKind == "reminder")) {
            Notifier.post(this, if (item.kind == ItemKind.APPROVAL) "Approval needed: ${item.title}" else item.title, item.body)
        }
    }

    /** Called by the notification listener. Dropped unless forwarding is on and this app is on the allow list. */
    fun forward(pkg: String, label: String, title: String, text: String) {
        scope.launch(Dispatchers.IO) {
            val p = settings.now()
            if (!p.forwardNotifications || pkg !in p.forwardPackages) return@launch
            val key = "$pkg|$title|$text"
            val now = SystemClock.elapsedRealtime()
            // Bounded: at most one per second, and an identical repeat within 10 s is ignored.
            if (now - lastForward < 1000 || (key == lastForwardKey && now - lastForward < 10_000)) return@launch
            lastForward = now; lastForwardKey = key
            val t = transport
            val shownTitle = Proto.truncate(title.ifBlank { label }, 60)
            if (t != null && hub.state.value.link == LinkState.ONLINE) {
                try {
                    t.postAlert(Proto.alertJson(label, "info", shownTitle, text, Priority.NORMAL))
                    hub.log("Sent a notification from $label to your computer")
                    return@launch
                } catch (_: Exception) { /* fall through: show it on the simulator instead */ }
            }
            hub.localAlert(shownTitle, Proto.truncate(text, 200), Priority.NORMAL, "forwarded", label)
        }
    }

    companion object {
        @Volatile private var inst: PibloApp? = null
        fun get() = inst
    }
}
