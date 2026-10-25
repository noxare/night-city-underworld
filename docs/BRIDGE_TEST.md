# Bridge-Test – Night City: Underworld 0.0.2

## Aufbau und Grenzen

CET sendet jeweils **eine Anfrage** über die feste Datei `bridge-request.json` an einen separaten Python-Worker. Der Worker schreibt in SQLite und legt danach atomar `bridge-response.json` ab. CET zeigt Ruf und Intel-Flags aus der Antwort des Python-Kerns an; Lua simuliert keine Änderungen vorab. Die Oberfläche zeigt **„Python-Kern: verbunden“** anhand eines Heartbeats und den Ruf als **„Ruf vom Python-Kern“**.

Der Runtime-Ordner liegt unter `%LOCALAPPDATA%\NightCityUnderworld\bridge`. Der Worker läuft dort separat im Hintergrund. Zum Start `%LOCALAPPDATA%\NightCityUnderworld\Start-UnderworldBridge.cmd` ausführen; zum kontrollierten Stoppen den danebenliegenden `Stop-UnderworldBridge.cmd` verwenden. Beim Windows-Neustart startet der Worker noch nicht automatisch. Es ist ein separater Demo-Kontext: Es gibt keine Synchronisierung mit Kampagnen-Spielständen. Das Journal aus 0.0.1 bleibt erhalten, wird aber nicht automatisch importiert. Ohne Worker gibt es keine Offline-Simulation.

## Update und Menü

1. Runtime und CET-Moddateien gemäß Paket bereitstellen; den Worker mit `Start-UnderworldBridge.cmd` starten.
2. Da das Spiel mit Prototype 0.0.1 bereits laufen kann: Im CET-Overlay **Reload all mods** wählen, das Overlay schließen und erneut öffnen.
3. Prüfen, dass die Oberfläche **Bridge 0.0.2** sowie die Statusanzeige **„Python-Kern: verbunden“** zeigt. Prüfen, ob **„Ruf vom Python-Kern“** und die Intel-Flags angezeigt werden.

## Ereignisse und Zustand prüfen

1. **Kontakt helfen (+15)** wählen. Nach der Worker-Antwort muss der angezeigte Kern-Ruf um 15 steigen; Lieferung wird freigeschaltet.
2. **Letztes Ereignis wiederholen** wählen. Die Antwort darf den Ruf nicht nochmals erhöhen.
3. **Lieferung untersuchen** wählen und danach **Klinik aufdecken**. Die jeweiligen Aktionen müssen nach ihrer Antwort die zugehörigen Intel-Flags freischalten.
4. **Kontakt schaedigen (-20)** wählen und prüfen, dass der Ruf erst nach der Antwort um 20 sinkt.
5. **Status vom Kern laden** wählen. Die Anzeige muss Ruf und Flags aus dem persistenten Kernzustand wiedergeben.
6. CET-Mods neu laden oder das Spiel neu starten; Worker weiterlaufen lassen und den Status erneut laden. Ruf und Flags sollten aus SQLite wiederhergestellt werden.

## Worker-Ausfall und Wiederholung

- Worker kontrolliert pausieren oder stoppen und im Spiel eine Aktion sowie **„Status vom Kern laden“** prüfen. Die Anzeige soll offline melden und das Spiel nicht einfrieren. Keine beliebigen Python-Prozesse über den Task-Manager beenden.
- Worker mit `Start-UnderworldBridge.cmd` wieder starten und eine ausstehende Anfrage sicher erneut versuchen. Wiederholungen dürfen Ruf oder Intel-Fortschritt nicht doppelt anwenden.
- Bei fehlender Verbindung Runtime-Worker-Log und CET-Mod-Log sichern. Den genauen Schritt und die sichtbare Statusanzeige notieren.

## Bericht

Notieren: ob 0.0.2 sichtbar wurde, Heartbeat-Status, Ruf/Flags vor und nach jeder Antwort, Verhalten beim Replay und Reload, Worker-Status sowie relevante Logzeilen. Die Engine-Integration ist noch nicht als im Spiel verifiziert bestätigt; Menü, Dateiaustausch und Zustandsanzeige benötigen diesen Test.

## Transportgrenzen
Anfragen und Antworten sind auf 16 KiB begrenzt. CET liest maximal viermal pro Sekunde, ohne Warteschleife im Spiel. Python bestaetigt ein Ereignis erst nach dem SQLite-Commit; seine Antwort wird atomar ersetzt. Bei einer verlorenen Antwort verwendet ein Retry dieselbe Ereignis-ID. Ein durch Reload unterbrochener Request wird wiederaufgenommen. Ein Worker-Lock verhindert zwei Schreiber am selben Postfach. Maximal 100 Demo-Ereignisse.
