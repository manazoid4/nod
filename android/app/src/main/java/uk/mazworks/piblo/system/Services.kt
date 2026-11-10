package uk.mazworks.piblo.system

import android.app.Notification
import android.app.Service
import android.content.Context
import android.content.Intent
import android.content.pm.ServiceInfo
import android.os.Build
import android.os.IBinder
import android.service.notification.NotificationListenerService
import android.service.notification.StatusBarNotification
import androidx.core.content.ContextCompat
import uk.mazworks.piblo.PibloApp

/** Only keeps the process alive (with a visible notification) so the poller in PibloApp can reach approvals while the app is closed. */
class WatchService : Service() {
    override fun onBind(i: Intent?): IBinder? = null
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        Notifier.channels(this)
        val n: Notification = Notifier.watching(this)
        if (Build.VERSION.SDK_INT >= 29) startForeground(1, n, ServiceInfo.FOREGROUND_SERVICE_TYPE_DATA_SYNC) else startForeground(1, n)
        return START_STICKY
    }

    companion object {
        fun set(ctx: Context, on: Boolean) {
            val i = Intent(ctx, WatchService::class.java)
            // Android 12+ refuses to start a foreground service from the background (e.g. process revived by an alarm): the next app open retries.
            try { if (on) ContextCompat.startForegroundService(ctx, i) else ctx.stopService(i) } catch (_: RuntimeException) {}
        }
    }
}

/**
 * Opt-in. Android only binds this after the person turns on "Notification access" for Piblo in system settings,
 * and PibloApp.forward() still drops anything whose app is not on the allow list.
 */
class PibloNotificationListener : NotificationListenerService() {
    override fun onNotificationPosted(sbn: StatusBarNotification) {
        val app = PibloApp.get() ?: return
        if (sbn.packageName == packageName || sbn.isOngoing) return
        val n = sbn.notification
        if (n.flags and Notification.FLAG_GROUP_SUMMARY != 0) return
        val extras = n.extras
        val title = extras.getCharSequence(Notification.EXTRA_TITLE)?.toString().orEmpty()
        val text = (extras.getCharSequence(Notification.EXTRA_BIG_TEXT) ?: extras.getCharSequence(Notification.EXTRA_TEXT))?.toString().orEmpty()
        val label = try { packageManager.getApplicationLabel(packageManager.getApplicationInfo(sbn.packageName, 0)).toString() } catch (_: Exception) { sbn.packageName }
        app.forward(sbn.packageName, label, title, text)
    }
}
