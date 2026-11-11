package uk.mazworks.piblo

import android.content.Intent
import android.os.Bundle
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.json.JSONObject
import uk.mazworks.piblo.data.Prefs
import uk.mazworks.piblo.data.SecretBox
import uk.mazworks.piblo.proto.CoreClient

/** Android's text share target uses the same paired Core client as the app. */
class ShareActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        if (intent.action != Intent.ACTION_SEND) { finish(); return }
        val text = intent.getCharSequenceExtra(Intent.EXTRA_TEXT)?.toString().orEmpty().trim()
        val title = intent.getStringExtra(Intent.EXTRA_SUBJECT).orEmpty().take(200)
        if (text.isBlank() || text.length > 50_000) {
            Toast.makeText(this, "Share text or a link to Piblo.", Toast.LENGTH_LONG).show()
            finish()
            return
        }
        lifecycleScope.launch {
            val saved = withContext(Dispatchers.IO) {
                try {
                    val prefs = (application as PibloApp).settings.now()
                    check(prefs.mode == Prefs.Mode.COMPUTER && prefs.hasComputer)
                    val token = SecretBox.decrypt(prefs.tokenBlob) ?: error("pairing_required")
                    val url = Regex("https?://[^\\s]+").find(text)?.value.orEmpty()
                    val body = JSONObject().put("text", text).put("title", title).put("url", url)
                    CoreClient(prefs.coreUrl, token, BuildConfig.VERSION_NAME).share(body.toString())
                    true
                } catch (_: Exception) { false }
            }
            Toast.makeText(this@ShareActivity,
                if (saved) "Saved to Piblo." else "Couldn't save. Open Piblo and check your computer connection.",
                Toast.LENGTH_LONG).show()
            finish()
        }
    }
}
