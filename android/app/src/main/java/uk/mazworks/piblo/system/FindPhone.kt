package uk.mazworks.piblo.system

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.media.AudioAttributes
import android.media.AudioManager
import android.media.MediaPlayer
import android.media.RingtoneManager
import android.os.Handler
import android.os.Looper
import uk.mazworks.piblo.PibloApp

/** Loud looping alarm on the alarm stream (rings even on silent/vibrate, as Find My Phone must). Stops on request or after 5 minutes. */
object FindPhone {
    private const val AUTO_STOP_MS = 5 * 60_000L
    private var player: MediaPlayer? = null
    private var savedVolume = -1
    private val main = Handler(Looper.getMainLooper())
    private val autoStop = Runnable { PibloApp.get()?.let { stop(it) } }

    @Synchronized fun start(ctx: Context) {
        if (player != null) return
        val app = ctx.applicationContext
        val am = app.getSystemService(AudioManager::class.java)
        savedVolume = am.getStreamVolume(AudioManager.STREAM_ALARM)
        am.setStreamVolume(AudioManager.STREAM_ALARM, am.getStreamMaxVolume(AudioManager.STREAM_ALARM), 0)
        val uri = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_ALARM) ?: RingtoneManager.getDefaultUri(RingtoneManager.TYPE_RINGTONE)
        player = try {
            MediaPlayer().apply {
                setAudioAttributes(AudioAttributes.Builder().setUsage(AudioAttributes.USAGE_ALARM).setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION).build())
                setDataSource(app, uri)
                isLooping = true
                prepare()
                start()
            }
        } catch (e: Exception) { restoreVolume(am); null }
        if (player != null) {
            Notifier.findPhone(app)
            PibloApp.get()?.hub?.setRinging(true)
            main.postDelayed(autoStop, AUTO_STOP_MS)
        }
    }

    @Synchronized fun stop(ctx: Context) {
        main.removeCallbacks(autoStop)
        player?.let { runCatching { it.stop() }; it.release() }
        player = null
        val app = ctx.applicationContext
        restoreVolume(app.getSystemService(AudioManager::class.java))
        Notifier.clearFind(app)
        PibloApp.get()?.hub?.setRinging(false)
    }

    private fun restoreVolume(am: AudioManager) {
        if (savedVolume >= 0) am.setStreamVolume(AudioManager.STREAM_ALARM, savedVolume, 0)
        savedVolume = -1
    }
}

class StopFindReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) { FindPhone.stop(context) }
}
