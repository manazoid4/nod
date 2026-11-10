package uk.mazworks.piblo.system

import android.Manifest
import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import androidx.core.app.NotificationCompat
import androidx.core.content.ContextCompat
import uk.mazworks.piblo.MainActivity
import uk.mazworks.piblo.R

object Notifier {
    const val CH_ALERTS = "alerts"
    const val CH_WATCH = "watch"
    const val CH_FIND = "find_phone"
    private const val ID_WATCH = 1
    const val ID_FIND = 2
    private var nextId = 100

    fun channels(ctx: Context) {
        val nm = ctx.getSystemService(NotificationManager::class.java)
        nm.createNotificationChannel(NotificationChannel(CH_ALERTS, "Piblo alerts and reminders", NotificationManager.IMPORTANCE_HIGH))
        nm.createNotificationChannel(NotificationChannel(CH_WATCH, "Watching your computer", NotificationManager.IMPORTANCE_LOW))
        nm.createNotificationChannel(NotificationChannel(CH_FIND, "Find my phone", NotificationManager.IMPORTANCE_HIGH).apply { setSound(null, null) })
    }

    fun canNotify(ctx: Context) = Build.VERSION.SDK_INT < 33 ||
        ContextCompat.checkSelfPermission(ctx, Manifest.permission.POST_NOTIFICATIONS) == PackageManager.PERMISSION_GRANTED

    private fun open(ctx: Context) =
        PendingIntent.getActivity(ctx, 0, Intent(ctx, MainActivity::class.java).addFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP), PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT)

    fun post(ctx: Context, title: String, body: String) {
        if (!canNotify(ctx)) return
        val n = NotificationCompat.Builder(ctx, CH_ALERTS).setSmallIcon(R.drawable.ic_stat).setContentTitle(title).setContentText(body)
            .setStyle(NotificationCompat.BigTextStyle().bigText(body)).setAutoCancel(true).setContentIntent(open(ctx))
            .setPriority(NotificationCompat.PRIORITY_HIGH).setCategory(NotificationCompat.CATEGORY_REMINDER).build()
        val id = nextId
        nextId = if (nextId >= 9000) 100 else nextId + 1
        ctx.getSystemService(NotificationManager::class.java).notify(id, n)
    }

    fun watching(ctx: Context): Notification =
        NotificationCompat.Builder(ctx, CH_WATCH).setSmallIcon(R.drawable.ic_stat).setContentTitle("Piblo is watching your computer")
            .setContentText("Approvals and alerts will reach this phone.").setOngoing(true).setContentIntent(open(ctx)).build()

    const val ACTION_STOP_FIND = "uk.mazworks.piblo.STOP_FIND"

    fun findPhone(ctx: Context) {
        val stop = PendingIntent.getBroadcast(ctx, 1, Intent(ctx, StopFindReceiver::class.java).setAction(ACTION_STOP_FIND), PendingIntent.FLAG_IMMUTABLE)
        val n = NotificationCompat.Builder(ctx, CH_FIND).setSmallIcon(R.drawable.ic_stat).setContentTitle("Piblo is ringing your phone")
            .setContentText("Tap Stop to silence it.").setOngoing(true).setContentIntent(open(ctx))
            .addAction(0, "Stop", stop).setPriority(NotificationCompat.PRIORITY_MAX).setCategory(NotificationCompat.CATEGORY_ALARM).build()
        if (canNotify(ctx)) ctx.getSystemService(NotificationManager::class.java).notify(ID_FIND, n)
    }

    fun clearFind(ctx: Context) = ctx.getSystemService(NotificationManager::class.java).cancel(ID_FIND)
}
