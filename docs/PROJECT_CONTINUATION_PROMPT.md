# Project continuation prompt

Setze Night City: Underworld im Repository noxare/night-city-underworld eigenständig fort.

Lies zuerst AGENTS.md, docs/DEVELOPMENT_STATUS.md, Architektur, Game Design,
Roadmap und die vorhandenen Agentenprofile/Playbooks. Prüfe aktuellen main,
offene PRs, relevante Actions und den realen Windows-Runtime-Stand. Nutze
docs/agents/COORDINATION.md zur aufgabenbezogenen Delegation. Aktuelle
Repository-Inhalte haben Vorrang vor älteren Chat-Zusammenfassungen.

Aktueller Schwerpunkt: echte verletzte NPC-Fortbewegung einschließlich Flucht.
Beziehe den Animation-Spezialisten, docs/ANIMATION_RESEARCH.md und
docs/playbooks/ANIMATION_LOCOMOTION.md ein. Verfolge vorhandene installierte
Animations-/Behavior-Ressourcen vollständig bis zur Aktivierung, statt weitere
Walk/Run- oder Statuseffekt-Vermutungen einzubauen. Ein verletzter NPC flieht so
schnell wie seine Verletzung erlaubt, langsamer als gesund und weiterhin sichtbar
humpelnd. Langsames normales Gehen oder gesundes Rennen erfüllt die Anforderung nicht.
Player- und NPC-Animationen getrennt behandeln.

Delegiere unabhängige Aufgaben gezielt: Engine/Animation, Kernlogik, Bridge/
Persistenz, Dashboard sowie Review/Runtime. Nutze kleinere verfügbare Modelle für
Routinearbeit und Experten für komplexe Engine-, Architektur- und Datenfragen.
Verwende nur tatsächlich verfügbare Modelle/Worker. Jeder Agent erhält ein klares
Ziel, eigene Dateien und einen überprüfbaren Übergabeauftrag. Du verantwortest
Integration und Abschluss.

Arbeite in zusammenhängenden Meilensteinen bis einschließlich relevanter Tests,
Review, Merge und reversibler Installation. Bewahre Spielstände, Daten und fremde
Mods. Teste Eingriffe zuerst nur an eigenen markierten Test-NPCs. Übernimm die
internen Zwischentests; fordere nicht nach jedem kleinen Schritt Nutzertests an.
Frage nur bei einer konkreten nötigen Nutzerhandlung oder bei der Abnahme eines
vollständigen Ingame-Pakets. Arbeite während eines noch offenen Engine-Punkts an
unabhängigen sinnvollen Aufgaben weiter.

Unterscheide streng: geplant, implementiert, intern getestet, installiert und
sichtbar im Spiel bestätigt. Keine erfundenen APIs, Animationsnamen oder fertigen
Funktionen. Dokumentiere echte Blocker und genaue nächste Schritte. Halte den
Fortschritt im Repository fest, damit ein Chatabbruch keinen Neustart der Arbeit
erfordert. Gib gelegentlich kurze sachliche Fortschrittsmeldungen und am Ende
Ergebnis, Nachweise und tatsächliche Grenzen an.
