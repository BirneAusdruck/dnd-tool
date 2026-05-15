# DnD VTT – Architektur & Migrationsphasen

## Zielarchitektur

```
data/                          ← Raw JSON Content (READ ONLY)
src/
  shared/
    repositories/
    domain/
    factories/
    runtime/
    services/
    systems/

  client/
    gui/

  server/
    vtt/
    chat/
    dice/
    rooms/
```

---

## Layer Definitionen

### 1. Data Layer (Raw Content)
- Enthält ausschließlich JSON-Dateien
- `data/classes/`, `data/spells/`, `data/items/`, …
- ❌ Keine Logik
- ❌ Keine Interpretation

### 2. Repository Layer (Data Access)
Bestehender `srd_loader.py` gehört hierhin → wird refactored zu `srd_repository.py`

Verantwortlichkeiten:
- Laden von JSON-Daten
- Mergen von Editionen (SRD, PHB, Custom)
- Filtern und Indexzugriff
- Caching von Rohdaten

⚠️ Gibt ausschließlich rohe Dictionaries zurück — enthält **keine** Game Logic.

### 3. Domain Layer
Wandelt rohe JSON-Daten in Domain Objects um.

Beispiele: `ClassDefinition`, `SpellDefinition`, `FeatDefinition`, `ItemDefinition`

Verantwortlichkeiten:
- Kapselung von D&D-Regeln
- Berechnungen (Progression, Scaling, Feature Logic)
- Strukturierung von Spielmechaniken
- ❌ Kein Filesystem-Zugriff
- ❌ Kein Runtime State

### 4. Factory Layer
Erzeugt Domain Objects aus Repository-Daten.

Beispiele: `ClassFactory`, `SpellFactory`, `FeatFactory`, `ItemFactory`

Verantwortlichkeiten:
- Mapping: `dict → Domain Object`
- Standardisierung der Objekt-Erstellung
- ❌ Keine Game Logic (nur Konstruktion)

### 5. Service Layer
Zentrale API für Domain Object Erstellung mit Cache und Lazy Loading.

Beispiel:
```python
ClassService.get("fighter")  # → ClassDefinition (via Factory + Repository + Cache)
```

Verantwortlichkeiten:
- Einziger Einstiegspunkt für Domain Objects von außen
- Cache Management
- Lazy Loading
- Zugriffskontrolle

### 6. Runtime Layer (Game State)
Repräsentiert aktive Spielsituationen.

Beispiele: `Character`, `CombatEncounter`, `ActiveEffect`

Verantwortlichkeiten:
- Mutable State
- Referenziert Domain Objects
- Enthält aktuellen Spielzustand

### 7. Systems Layer (Rules Engine)
Enthält alle Spielmechaniken.

Beispiele: `CombatSystem`, `LevelUpSystem`, `DiceSystem`, `EffectResolutionSystem`

Regeln:
- Arbeitet ausschließlich mit Domain + Runtime Objekten
- ❌ Kein Zugriff auf JSON oder Repository Layer
- ❌ Keine Persistenzlogik

---

## Architekturprinzipien

### ❌ Verboten
- UI greift direkt auf JSON zu
- Server interpretiert JSON direkt
- Repository enthält Game Rules
- Domain enthält Runtime State Logic
- `dict`-basierte Charaktere im gesamten System

### ✅ Erlaubt
- `data → repository → factory → domain → runtime → systems`
- Client und Server teilen Domain Layer
- Data Layer ist READ ONLY
- Klare Trennung von Simulation und Darstellung

---

## Migrationsphasen

### PHASE 0 – Stabilisierung
> Keine Logik ändern, nur strukturieren und verstehen.

Betroffene Bereiche:
- `src/models/*`
- `src/srd_loader.py`
- `src/game/*`
- `data/*`

---

### PHASE 1 – Persistence Layer
```
src/models/  →  src/persistence/models/
```

---

### PHASE 2 – Domain Root
```
src/game/  →  src/shared/domain/
```
Oder direkt neu strukturieren unter `src/shared/domain/`.

---

### PHASE 3 – Domain Definitions (NEU)
Neue Dateien unter `src/shared/domain/definitions/`:
- `ClassDefinition`
- `SpellDefinition`
- `FeatDefinition`
- `ItemDefinition`

---

### PHASE 4 – Repository Refactor
```
src/srd_loader.py  →  src/shared/repositories/srd_repository.py
```

Änderungen:
- Bleibt Data Access Layer
- Gibt nur `dict` zurück
- Alle Rule Functions werden entfernt

---

### PHASE 5 – Factory Layer (NEU)
Neue Dateien unter `src/shared/factories/`:
- `ClassFactory`
- `SpellFactory`
- `FeatFactory`
- `ItemFactory`

---

### PHASE 6 – Service Layer (NEU)
Neue Dateien unter `src/shared/services/`:
- `ClassService`
- `SpellService`
- `ItemService`

Jeder Service: Cache + Lazy Loading via Factory + Repository.

---

### PHASE 7 – Runtime Layer (NEU)
Neue Dateien unter `src/shared/runtime/`:
- `Character`
- `CombatEncounter`
- `ActiveEffect`

---

### PHASE 8 – Systems Layer (NEU)
Neue Dateien unter `src/shared/systems/`:
- `CombatSystem`
- `LevelUpSystem`
- `DiceSystem`
- `EffectResolutionSystem`

---

### PHASE 9 – Client Isolation
```
src/gui/  →  src/client/gui/
```

---

### PHASE 10 – Server Isolation
Struktur unter `src/server/`:
```
vtt/
chat/
dice/
rooms/
```

---

### PHASE 11 – Shared Entry Point
```python
# src/shared/__init__.py
# Exportiert alle öffentlichen Domain Objects, Services und Systems
```

---

## Ziel der Architektur

Diese Struktur ist notwendig für:
- Skalierbare VTT-Architektur
- Stabile Multiplayer-Synchronisation
- Klare Rule Engine Trennung
- Homebrew / Modding Support
- Zukünftige AI / Automation Features
- Testbare und deterministische Game Logic
