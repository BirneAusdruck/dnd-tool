# 📚 Git Grundlagen – Befehlsreferenz

> Diese README dient als Vorlage und Nachschlagewerk für alle Git-Projekte.

---

## Inhaltsverzeichnis

1. [Konfiguration](#konfiguration)
2. [Repository anlegen](#repository-anlegen)
3. [Status & Überblick](#status--überblick)
4. [Dateien stagen & committen](#dateien-stagen--committen)
5. [Branches](#branches)
6. [Remote-Repositories](#remote-repositories)
7. [Änderungen zusammenführen](#änderungen-zusammenführen)
8. [Verlauf & Logs](#verlauf--logs)
9. [Rückgängig machen & Zurücksetzen](#rückgängig-machen--zurücksetzen)
10. [Stash – Änderungen zwischenparken](#stash--änderungen-zwischenparken)
11. [Tags](#tags)
12. [Nützliche Hilfsbefehle](#nützliche-hilfsbefehle)

---

## Konfiguration

Einmalige Einrichtung von Name und E-Mail (wird in jedem Commit gespeichert).

```bash
git config --global user.name "Dein Name"
git config --global user.email "deine@email.de"

# Standard-Editor festlegen (z.B. VS Code)
git config --global core.editor "code --wait"

# Standard-Branch-Name auf "main" setzen
git config --global init.defaultBranch main

# Aktuelle globale Konfiguration anzeigen
git config --list
```

---

## Repository anlegen

```bash
# Neues lokales Repository erstellen
git init

# Bestehendes Remote-Repository klonen
git clone https://github.com/user/repo.git

# Klonen in einen bestimmten Ordner
git clone https://github.com/user/repo.git mein-ordner
```

---

## Status & Überblick

```bash
# Aktuellen Status anzeigen (geänderte, gestagede, ungetrackte Dateien)
git status

# Kurze Statusübersicht
git status -s

# Unterschiede im Arbeitsverzeichnis anzeigen (noch nicht gestaged)
git diff

# Unterschiede im Stage-Bereich anzeigen (bereits gestaged, noch nicht committed)
git diff --staged
```

---

## Dateien stagen & committen

```bash
# Einzelne Datei stagen
git add datei.txt

# Alle geänderten Dateien stagen
git add .

# Interaktiv einzelne Teile einer Datei stagen
git add -p datei.txt

# Commit mit Nachricht erstellen
git commit -m "Kurze, aussagekräftige Beschreibung"

# Stagen und Committen in einem Schritt (nur bereits getrackte Dateien)
git commit -am "Nachricht"

# Letzten Commit nachträglich ändern (Nachricht oder Inhalt)
git commit --amend -m "Korrigierte Nachricht"

# Datei aus dem Stage-Bereich entfernen (unstagen)
git restore --staged datei.txt

# Änderungen an einer Datei verwerfen (Arbeitsverzeichnis zurücksetzen)
git restore datei.txt

# Datei aus dem Repository und vom Dateisystem entfernen
git rm datei.txt

# Datei nur aus Git entfernen, aber lokal behalten
git rm --cached datei.txt
```

---

## Branches

```bash
# Alle lokalen Branches anzeigen
git branch

# Alle Branches anzeigen (lokal + remote)
git branch -a

# Neuen Branch erstellen
git branch feature/mein-feature

# Zu einem Branch wechseln
git switch feature/mein-feature

# Branch erstellen und direkt wechseln
git switch -c feature/mein-feature

# Aktuellen Branch umbenennen
git branch -m neuer-name

# Branch löschen (nur wenn gemergt)
git branch -d feature/mein-feature

# Branch löschen (erzwungen, auch ungemergt)
git branch -D feature/mein-feature
```

---

## Remote-Repositories

```bash
# Lokales Repo zum ersten Mal auf GitHub veröffentlichen
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/user/repo.git
git push -u origin main

# Verbundene Remote-Repos anzeigen
git remote -v

# Remote hinzufügen
git remote add origin https://github.com/user/repo.git

# Remote umbenennen
git remote rename origin upstream

# Remote entfernen
git remote remove origin

# Änderungen auf Remote hochladen
git push origin main

# Beim ersten Push Tracking setzen
git push -u origin main

# Änderungen vom Remote holen und mergen
git pull origin main

# Nur holen, nicht mergen (sicherer)
git fetch origin

# Alle Remote-Branches holen
git fetch --all
```

---

## Änderungen zusammenführen

```bash
# Branch in aktuellen Branch mergen
git merge feature/mein-feature

# Merge ohne Fast-Forward (erzeugt immer einen Merge-Commit)
git merge --no-ff feature/mein-feature

# Änderungen per Rebase integrieren (saubere, lineare Historie)
git rebase main

# Interaktiver Rebase (z.B. letzte 3 Commits bearbeiten)
git rebase -i HEAD~3

# Merge abbrechen (bei Konflikten)
git merge --abort

# Rebase abbrechen
git rebase --abort

# Einzelnen Commit aus einem anderen Branch übernehmen
git cherry-pick abc1234
```

> **Merge vs. Rebase:**
> - `merge` bewahrt die vollständige Commit-Historie, erzeugt aber Merge-Commits.
> - `rebase` erzeugt eine lineare Historie, überschreibt aber Commits – **nie auf geteilten Branches rebased!**

---

## Verlauf & Logs

```bash
# Commit-Verlauf anzeigen
git log

# Kompakt: eine Zeile pro Commit
git log --oneline

# Als Graph mit Branches darstellen
git log --oneline --graph --all

# Änderungen eines bestimmten Commits anzeigen
git show abc1234

# Wer hat welche Zeile zuletzt geändert?
git blame datei.txt

# Suche: Wann wurde ein bestimmter Begriff eingeführt/entfernt?
git log -S "suchbegriff"

# Verlauf einer einzelnen Datei anzeigen
git log -- datei.txt
```

---

## Rückgängig machen & Zurücksetzen

```bash
# Commit rückgängig machen (erzeugt neuen Revert-Commit, sicher für geteilte Branches)
git revert abc1234

# HEAD auf einen früheren Commit setzen, Änderungen bleiben im Stage-Bereich
git reset --soft HEAD~1

# HEAD zurücksetzen, Stage-Bereich wird geleert (Standard)
git reset --mixed HEAD~1

# Alles zurücksetzen – Commits UND Arbeitsverzeichnis (Vorsicht: Datenverlust!)
git reset --hard HEAD~1

# Verloren geglaubte Commits wiederfinden
git reflog
```

> ⚠️ **`git reset --hard`** löscht Änderungen unwiderruflich. Vorher `git reflog` als Sicherheitsnetz kennen!

---

## Stash – Änderungen zwischenparken

Nützlich, wenn man den Branch wechseln muss, ohne unfertige Arbeit zu committen.

```bash
# Aktuelle Änderungen wegparken
git stash

# Mit einer Beschreibung stashen
git stash push -m "WIP: Login-Formular"

# Alle Stashes anzeigen
git stash list

# Letzten Stash wieder anwenden
git stash pop

# Bestimmten Stash anwenden
git stash apply stash@{2}

# Stash löschen
git stash drop stash@{0}

# Alle Stashes löschen
git stash clear
```

---

## Tags

```bash
# Alle Tags anzeigen
git tag

# Leichtgewichtigen Tag erstellen
git tag v1.0.0

# Annotierten Tag erstellen (empfohlen für Releases)
git tag -a v1.0.0 -m "Version 1.0.0"

# Tag auf Remote pushen
git push origin v1.0.0

# Alle Tags pushen
git push origin --tags

# Tag löschen (lokal)
git tag -d v1.0.0

# Tag löschen (remote)
git push origin --delete v1.0.0
```

---

## Nützliche Hilfsbefehle

```bash
# .gitignore-Muster testen (zeigt ignorierte Dateien)
git check-ignore -v datei.txt

# Alle ignorierten Dateien anzeigen
git status --ignored

# Arbeitsverzeichnis bereinigen (ungetrackte Dateien löschen)
git clean -fd

# Zwei Commits oder Branches vergleichen
git diff main..feature/mein-feature

# Commit finden, der einen Bug eingeführt hat (binäre Suche)
git bisect start
git bisect bad                # aktueller Commit ist fehlerhaft
git bisect good abc1234       # dieser Commit war noch gut
# → Git checkt automatisch Commits aus, bis der Übeltäter gefunden ist
git bisect reset              # Suche beenden
```

---

## Tipps für gute Commit-Nachrichten

```
Typ: Kurze Zusammenfassung (max. 72 Zeichen)

Optionaler längerer Beschreibungstext. Erkläre WAS und WARUM,
nicht WIE (das sieht man im Code).

Typen: feat | fix | docs | style | refactor | test | chore
```

**Beispiele:**
```
feat: Benutzeranmeldung per E-Mail hinzugefügt
fix: Absturz beim Laden leerer Listen behoben
docs: README mit Installationsanleitung ergänzt
refactor: Datenbankabfragen in eigene Klasse ausgelagert
```

---