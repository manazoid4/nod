package uk.mazworks.piblo.system

import android.app.AlarmManager
import android.app.PendingIntent
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.os.Build
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import uk.mazworks.piblo.PibloApp
import uk.mazworks.piblo.data.PibloDb
import uk.mazworks.piblo.data.Reminder
import uk.mazworks.piblo.proto.Priority

object ReminderScheduler {
    const val EXTRA_ID = "reminder_id"

    private fun pi(ctx: Context, id: Long) =
        PendingIntent.getBroadcast(ctx, id.toInt(), Intent(ctx, ReminderReceiver::class.java).putExtra(EXTRA_ID, id), PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT)

    fun canBeExact(ctx: Context) = Build.VERSION.SDK_INT < 31 || ctx.getSystemService(AlarmManager::class.java).canScheduleExactAlarms()

    fun schedule(ctx: Context, r: Reminder) {
        val am = ctx.getSystemService(AlarmManager::class.java)
        // Exact alarms need the person to allow "Alarms & reminders"; without it the system may delay a reminder by a few minutes.
        if (canBeExact(ctx)) am.setExactAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, r.atMs, pi(ctx, r.id))
        else am.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, r.atMs, pi(ctx, r.id))
    }

    fun cancel(ctx: Context, id: Long) = ctx.getSystemService(AlarmManager::class.java).cancel(pi(ctx, id))

    suspend fun rescheduleAll(ctx: Context) = PibloDb.get(ctx).dao().pendingReminders().forEach { schedule(ctx, it) }
}

class ReminderReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        val id = intent.getLongExtra(ReminderScheduler.EXTRA_ID, -1)
        val pending = goAsync()
        CoroutineScope(Dispatchers.IO).launch {
            try {
                val dao = PibloDb.get(context).dao()
                val r = dao.reminder(id)
                if (r != null && !r.done) {
                    dao.markDone(id)
                    val timer = r.kind == "timer"
                    // Shows on the (simulated) Piblo; PibloApp's HubEvents saves it to Messages and notifies when the app is closed.
                    PibloApp.get()?.hub?.localAlert(if (timer) "Timer done" else "Reminder", r.text, Priority.HIGH, "reminder", "reminders")
                }
            } finally { pending.finish() }
        }
    }
}

class BootReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action != Intent.ACTION_BOOT_COMPLETED) return
        val pending = goAsync()
        CoroutineScope(Dispatchers.IO).launch { try { ReminderScheduler.rescheduleAll(context) } finally { pending.finish() } }
    }
}
