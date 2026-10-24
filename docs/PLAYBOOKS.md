# Entwicklungs-Playbooks: Night City Underworld

## Modellwahl und Eskalation

- **Kleines Modell:** Dokumente zusammenfassen, klar begrenzte Unit-Tests ergänzen und wiederkehrende Diagnosen durchführen.
- **Hauptmodell:** Architekturentscheidungen, Engine-Hooks, Persistenz und Save-Rollback sowie Code-Reviews bearbeiten.
- Bei einem Fehlschlag höchstens **einen gezielten Retry** mit konkretem Fehlerbild durchführen; scheitert er erneut, an das Hauptmodell eskalieren.
- Modellwahl nur angeben, wenn die Umgebung sie tatsächlich unterstützt. **Keine lokale Ollama-Verfügbarkeit behaupten**, wenn sie nicht verifiziert ist.

## Arbeit wieder aufnehmen

1. `AGENTS.md`, `README` und vorhandene Architektur-, Design-, Roadmap- und Statusdokumente lesen.
2. Repository-Zustand und aktuellen Branch prüfen; Änderungen und offene Arbeitsstände feststellen.
3. Aktuellen Stand von `main`, relevanten PRs und CI-Ergebnissen prüfen, sofern diese Informationen im Arbeitskontext verfügbar sind.
4. Erst danach den nächsten Schritt aus Roadmap und tatsächlichem Codezustand ableiten. Vorhandene Änderungen nicht überschreiben.
5. Status knapp festhalten: erledigt, offen, Risiken und nächster konkreter Schritt.

## Windows-Mod-Crash diagnostizieren

1. Reproduktionsschritte, Spiel- und Mod-Versionen sowie Logs sichern; vor Änderungen Konfiguration und relevante Dateien sichern.
2. Immer **nur eine Variation auf einmal** ändern und nach jeder Änderung denselben Start- oder Reproduktionsablauf wiederholen.
3. Saves niemals löschen oder durch Testläufe überschreiben. Wenn ein Save nötig ist, mit einer gesicherten Kopie arbeiten.
4. Zwei Ergebnisse getrennt prüfen: **Prozessstatus** (Start, Absturz, Exit-Code/Log) und **sichtbares Verhalten** (Menü erreicht, Mod-Anzeige oder Funktion sichtbar).
5. Ein laufender Prozess beweist keine korrekte Mod-Initialisierung. Menü- oder Funktionsverhalten visuell verifizieren und Beobachtungen samt Logs dokumentieren.

## Core- und Bridge-Implementierung

1. Core und Engine-Bridge klar trennen. JSON-Nachrichten als versionierte Envelopes mit Schema-Version, Ereignistyp, stabiler ID und Nutzlast definieren.
2. Ereignisverarbeitung idempotent gestalten: wiederholte Zustellung darf Zustände nicht doppelt anwenden.
3. Save-Zugriffe isolieren; Schreibpfade und Rollback so gestalten, dass Fehler den bestehenden Spielstand nicht beschädigen. Tests mit temporären bzw. kopierten Daten durchführen.
4. Änderungen gezielt testen: Core-Unit-Tests für Logik und Serialisierung, Bridge-Tests für Mapping, Versionierung und Wiederholungen. Nur die betroffenen Bereiche ausführen und Ergebnisse notieren.
5. Keine Engine-Integration oder funktionierende CET-Anbindung behaupten, solange sie nicht im Spiel getestet wurde. Stand dieses Schritts: Python-Core/Store und lokaler JSONL-Übergang mit zehn Tests; CET-Anbindung noch nicht implementiert.

## Übergabe an die nächste Person

Eine Übergabe enthält immer:

- **Commits:** Hashes und kurze Beschreibung; falls uncommittet, betroffene Pfade nennen.
- **Änderungen:** relevante Dateien/Pfade und Verhalten.
- **Nachweise:** exakt ausgeführte Tests/CI und deren Ergebnis; Engine- oder Menüprüfung separat kennzeichnen.
- **Blocker:** fehlende Umgebung, unbelegte Annahmen und offene Fehler.
- **Nächster Schritt:** eine konkrete, direkt ausführbare Aktion.

Bekannter Stand: Plugin-Start war zuletzt geordnet; **CET ist damit nicht bestätigt**. Core/Store und JSONL-Übergang haben zehn Tests; CET-Anbindung fehlt.
