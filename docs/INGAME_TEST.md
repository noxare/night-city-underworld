# Ingame-Checkliste – Night City: Underworld 0.0.1

Dies ist der erste testbare UI- und Domänen-Prototyp. Es gibt noch kein NPC-Spawning, keinen Kampf, keine Quests und keinen angebundenen Python-Sidecar. Bitte prüfe besonders, ob CET das Mod-Menü lädt und die sichtbaren Aktionen wie beschrieben funktionieren.

## Start und Menü prüfen

1. Cyberpunk 2077 unter Windows starten und mit der üblichen CET-Overlay-Taste das Overlay öffnen.
2. Nach dem Fenster **„Night City: Underworld - Prototype“** suchen.
3. Prüfen, ob diese Schaltflächen sichtbar sind:
   - **Kontakt helfen (+15)**
   - **Lieferung untersuchen**
   - **Klinik aufdecken**
   - **Kontakt schaedigen (-20)**
   - **Letztes Ereignis wiederholen** (nach dem ersten Ereignis)
   - **V-Position aus Spiel lesen** (echte Koordinaten bei geladenem Spielstand)

## Aktionen prüfen

1. Zu Beginn sollten Lieferung und Klinik noch gesperrt sein.
2. **Kontakt helfen (+15)** wählen. Prüfen, dass der Ruf um 15 steigt und die Lieferung freigeschaltet wird.
3. **Lieferung untersuchen** wählen. Prüfen, dass die Klinik freigeschaltet wird.
4. **Klinik aufdecken** waehlen und den entdeckten Testkontakt pruefen.
5. **Kontakt schaedigen (-20)** wählen. Prüfen, dass der Ruf um 20 sinkt.
6. **Letztes Ereignis wiederholen** wählen. Prüfen, dass die Wiederholung protokolliert wird und den Ruf **nicht erneut ändert**.
7. Optional Mod-Status neu laden (alle Mods neu laden) oder das Spiel neu starten. Der Demo-Zustand sollte wiederhergestellt werden.

Die Ereignisse werden in `bin\x64\plugins\cyber_engine_tweaks\mods\night_city_underworld\demo-events.jsonl` gespeichert, getrennt von den Spielständen. Spielstände nicht löschen oder für diesen Test verändern.

## Wenn das Menü fehlt oder etwas nicht stimmt

- CET-Log auf Hinweise zum Laden des Mods oder Lua-Fehler prüfen. Den relevanten Logausschnitt und die genaue Reproduktion notieren.
- Nicht alle Frameworks neu installieren. Zuerst nur CET-Status, Mod-Ordner und Logeinträge prüfen.
- Sichtbares Verhalten im Spiel separat vom Prozessstatus melden: Ein laufendes Spiel beweist nicht, dass Menü und Mod korrekt geladen wurden.

Nach **Reload all mods** das CET-Overlay schliessen und erneut oeffnen, falls die Schaltflaechen fehlen. Ueber CET > Bindings > Underworld: Testfenster anzeigen laesst sich das Fenster ein-/ausblenden.

Ein globales Demo-Profil: Ein anderer/aelterer Spielstand setzt die Testdaten nicht zurueck. Keine Kampagnen-Synchronisierung. Limit 100 Ereignisse. Ein beschaedigtes/unvollstaendiges Journal blockiert weitere Schreibaktionen und bleibt erhalten. Die Lua-Regeln sind noch nicht mit dem externen Python-Kern verbunden.

## Technische Grundlage
Offizielle CET-Dokumentation: [onInit](https://wiki.redmodding.org/scripting-cyberpunk/cyber-engine-tweaks/cet-functions/events/oninit), [onDraw](https://wiki.redmodding.org/scripting-cyberpunk/cyber-engine-tweaks/cet-functions/events/ondraw), [Sandbox-IO](https://wiki.redmodding.org/cyber-engine-tweaks/patch-notes).
