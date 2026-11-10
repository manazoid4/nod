package uk.mazworks.piblo

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.testTag
import uk.mazworks.piblo.ui.ConnectionsScreen
import uk.mazworks.piblo.ui.HomeScreen
import uk.mazworks.piblo.ui.MessagesScreen
import uk.mazworks.piblo.ui.SettingsScreen
import uk.mazworks.piblo.ui.ToolsScreen

private val tabs = listOf("Home" to "⌂", "Messages" to "✉", "My Tools" to "✎", "Connections" to "⇄", "Settings" to "⚙")

private val Light = lightColorScheme(primary = Color(0xFF0B1B3A), onPrimary = Color(0xFFFFF6E9), secondary = Color(0xFFB88700), background = Color(0xFFFFF6E9), surface = Color(0xFFFFFBF5))
private val Dark = darkColorScheme(primary = Color(0xFFFFD23F), onPrimary = Color(0xFF0B1B3A), secondary = Color(0xFF4CE0B3), background = Color(0xFF0B1B3A), surface = Color(0xFF13264D))

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MaterialTheme(colorScheme = if (isSystemInDarkTheme()) Dark else Light) {
                var tab by rememberSaveable { mutableIntStateOf(0) }
                Scaffold(
                    bottomBar = {
                        NavigationBar {
                            tabs.forEachIndexed { i, (label, glyph) ->
                                NavigationBarItem(selected = tab == i, onClick = { tab = i }, icon = { Text(glyph) }, label = { Text(label, maxLines = 1) }, modifier = Modifier.testTag("tab_$label"))
                            }
                        }
                    },
                ) { pad ->
                    Surface(Modifier.padding(pad)) {
                        when (tab) {
                            0 -> HomeScreen()
                            1 -> MessagesScreen()
                            2 -> ToolsScreen()
                            3 -> ConnectionsScreen()
                            else -> SettingsScreen()
                        }
                    }
                }
            }
        }
    }
}
