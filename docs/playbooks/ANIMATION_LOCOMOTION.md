# Playbook: Animationen und verletzte Fortbewegung

## Gewünschtes Ergebnis
Ein NPC mit Beinverletzung bewegt sich sichtbar verletzt. Flucht erhöht seine
Dringlichkeit innerhalb der verletzungsbedingten Möglichkeiten: normalerweise
schneller als verletztes Gehen, langsamer als gesunde Flucht, weiterhin humpelnd.
Weder Walk als Ersatz für Humpeln noch uneingeschränktes Run erfüllt das Ziel.

## 1. Bestand und Evidenz sichern
- Spiel-, CET-, Codeware- und Adapterversion feststellen; vorhandene Logs lesen.
- Nutzerbeobachtung, synthetischen Test und reale Telemetrie getrennt erfassen.
- Laufende Prozesse/Installationspfade prüfen; vorhandene Daten erhalten.
- Einen ausführbaren internen Prüfplan wählen, nicht jede Recherche als
  Entscheidung an den Nutzer zurückreichen.

## 2. Vollständige Engine-Kette untersuchen
Arbeite von der gewünschten sichtbaren Wirkung rückwärts:
Animation/Animationssatz -> Graph/Feature -> Verhalten/Task -> AI-Rolle und
Bedingungen -> Ereignis/Status -> eigener Adapter.
Untersuche insbesondere:
- hit_reactions.behavior, wounded_entry_se.behavior und PainReactionTask;
- Statuseffekt-Datensatz samt zugehörigen Bedingungen und tatsächlichem Consumer;
- Crowd gegenüber regulärem NPC, Kampf/Deckung/Workspot und andere Ausschlüsse;
- Bewegungsabsicht, Navigation, Geschwindigkeitsgrenze und verletzte Gangart;
- Szenen-/Workspot-Animation gegenüber frei navigierender Locomotion;
- Skelett/Animationssatz und Kompatibilität mit dem gewählten Test-NPC.

Aktuelle Spielressourcen sind gegenüber älteren dekompilierten Quellen maßgeblich.
Eine ältere Quelle liefert einen überprüfbaren Ansatz und ist kein automatischer
Grund abzubrechen. Nutze vorhandenes WolvenKit/CLI oder Runner-Werkzeuge zum
Auflisten und gezielten Extrahieren der benötigten Ressourcen. Fehlende Werkzeuge
oder Zugriffe konkret feststellen; nicht eine vollständige Neuinstallation verlangen.
Keine Spielarchive oder fremden Assets ins öffentliche Repository kopieren.

## 3. Evidenzmatrix führen
Für jede relevante Ressource/API festhalten:
Name/Pfad, Primärquelle, Quellversion, installiert vorhanden, Aufruf akzeptiert,
Verhalten sichtbar, bekannte Ausschlüsse, Entfernen/Abbruch geprüft.
Ein vorhandener CrippledLeg-Datensatz beweist keine anhaltende Humpelbewegung.
Registrierter Hook beweist keine Auslösung. Ein Move-Befehl beweist keine Bewegung.
Keine mehrdeutige Animationsgruppe als eindeutige Körperzone deklarieren.

## 4. Zusammenhängenden Adapter bauen
- Nur eigenen markierten, begrenzt erzeugten Test-NPC verändern.
- AI-Verhalten, Gangart und Geschwindigkeit gemeinsam anbinden.
- Zustandsübergänge gesund -> verletzt -> Flucht -> Unterbrechung -> Fortsetzung
  -> Behandlung -> gesund implementieren.
- Verletzung bei neuer Bewegungsabsicht erhalten; nicht jeden Frame Animationen
  oder Status-Effekte neu starten. Voraussetzungen vor Änderung prüfen.
- Zustandsbesitz, Entfernung von Effekten, Abbruch, Entladen und Cleanup behandeln.
- NPC-Handles nicht als dauerhafte Identität speichern; Kampagnen-/Questakteure
  nicht automatisch übernehmen.
- Spieler-V und NPCs benötigen getrennte Adapter: Kamera, First-/Third-Person,
  Eingabe, Locomotion und Questzustände dürfen nicht vermischt werden.

## 5. Interne Prüfung und Auslieferung
- Zielgerichtete Tests für Übergänge, Wiederholung, Eigentum, Abbruch und Cleanup.
- Engine-/API-Fehler sichtbar melden; geschluckte Modulfehler verhindern.
- Tatsächliche Bewegung messen und unverfälschte Gangart separat beobachten.
- Nach CI installieren, Laufzeit/Heartbeat und Dateien prüfen.
- Ergebnisstatus ehrlich halten: Implementierung / installiert / Ingame bestätigt.
- Erst das vollständige Szenario zur Nutzerabnahme geben. Andere unabhängige
  Projektarbeiten dürfen parallel weiterlaufen.

## Gebündelte Abnahme
1. Gesunde Bewegung und Flucht als Vergleich.
2. Linke/rechte Beinverletzung: sichtbare Gangart plus gemessene Bewegung.
3. Verletzte Flucht: höhere Dringlichkeit, reduzierte Fähigkeiten, kein Rücksprung
   auf gesunde Gangart.
4. Unterbrechung/Neuer Befehl erhält Verletzung.
5. Behandlung und vollständiges Aufräumen ohne hängenbleibende AI/Effekte.

## Bekannte Ansatzpunkte, keine abgeschlossene Lösung
- Modding-Dokumentation beschreibt wounded_entry_se.behavior als Teil der
  Hit-Reaction-Verhaltenskette mit verletzten Bewegungen.
- Öffentliche dekompilierte HitReactionComponent-Quelle stammt aus 2.11:
  CrippledLegLeft/Right und Pain sind Ansatzpunkte für installierte 2.5-Prüfung.
- Der bisherige Crowd-Klon plus CrippledLeg und MoveTo hat die gewünschte Gangart
  im Nutzertest nicht bestätigt. Dieses Ergebnis erfordert Ursachenanalyse,
  keine Umbenennung des Tests in eine fertige Verletzungsfunktion.

Primärquellen:
https://github.com/CDPR-Modding-Documentation/Cyberpunk-Modding-Docs
https://github.com/CDPR-Modding-Documentation/Cyberpunk-Scripts
https://github.com/psiberx/cp2077-codeware
https://github.com/maximegmd/CyberEngineTweaks
