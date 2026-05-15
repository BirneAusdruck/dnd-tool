# Umbau der Json Datenbank

## Phase 1:
Die json Dateien unter Data werden nun erwitert, so das diese konsistent mit den definitions sind. Zuerst wird mit srd 5.2 gearbeitet und dann mit srd 5.1. Prüfe die Gui nicht denn diese ist noch nicht fertig. Konzentriere dich nur auf die Definitions, Jsons Factories und Services.
Die Reihenfolge der zu bearbeitenden json Dateien ist wie folgt:

### Schritt 1: armor.json
### Schritt 2: background.json
### Schritt 3: classes.json
### Schritt 5: equipment.json
### Schritt 6: feats.json
### Schritt 7: magic-items.json
### Schritt 8: races.json
### Schritt 9: spells.json
### Schritt 10: weapons.json

## Phase 2:
In Phase 2 geht es um die granulare Strukturierung der json Dateien. Hierbei steht das Custom Content Creator feature im Fokus. Ziel ist es alle eigenen Entitäten in den json Datein zu kapseln, so dass es möglich ist, anhand der modularen Software Architektur, eigenständigen Content zu erstellen. Dieses Feature ist noch nicht implementiert, hier wird lediglich der Grundstein dafür gelegt. Dabei werden, wie in den folgendne Schritten erläutert, alle auszulagernden Entitäten in einzelne json Datein formatiert, wobei dies nach dem Vorbild der schon vorhanden json Dateien zu gestalten ist. Falls Einträge, Dateien oder Logik fehlen müssen diese erstellt werden. Wichtig ist auch das für jede json Datei ein Service bereitgestellt werden muss. Überprüfe auch die repository Schicht auf notwendige anpassungen.

### Schritt 1: backgrounds.json
- equipment: list[dict[str, str]] -> index_string. Auslagern in background_equipment_entries.json wobei equipment ein index feld dazu bekommt.
- feature: dict[str, str] -> index_string. auslagern in background_features.json wobei feature ein index feld hinzu bekommt.
- personality_traits: list[str] -> list[index_string]. ausgelagert in background_personality_traits.json in der struktur dict[str, list[str]] pro entität.
- ideals, bonds und flaws analog zu personality_traits

### Schritt 2: classes.json
- subclasses: list[str] -> list[index_string]. ausgelagert in subclasses.json. die struktur erhält ebenfalls einen index und der subclass_name wird ebenfalls aus der classes.json als oberstru## Schritt 6: classes.jsonkur in die subclasses integriert. Es soll wie folgt aussehen: 
"subclass_name_index": index_string,
"subclass_name": gui_name,
    ["subclass_index": index_string,
    "subclass": gui_name,]
- starting_equipment soll ebenfalls ausgelagert werden in class_starting_equipments.json.
- features verdient wie feat ein eigne featuers.json Datei und soll damit auch ausgelagert werden. Achtung innerhalb von feature wie auch in einigen anderen entitäten kommen effects vor, diese sollen auch ausgelagert werden in effects.json und dann per index_string auf die richtige stelle verweisen.

### Schritt 3: equipment.json
- hier müssen die effects in die aus `Schritt 2` erzeugte effects.json überführt werden

### Schritt 4: feats.json
- hier soll der prerequisites_mode in die Prerequisites Oberklasse integriert werden welche dann an alle anderen Prerequisites klassen vererbt wird. Damit wird dann auch der TypeAlias Prerequisites in der feat_definition.py überflüssig und kann entfernt werden.

### Schritt 5: magic-items.json
- das attunement feld muss besser strukturiert werden. Das Feld soll in eine list[str] umgewandelt werden wobei die strings indizes auf die indexe von klassen verweist oder das keyword any hat fall es keine klassen beschränkung gibt. None bleibt weiterhin als wert falls das item kein attunement benötigt.
- Auch ganz wichtig ist das magic-items ein feld für effects braucht. diese Feld wird, wie vorher auch, mit indizes auf die effects.json verwissen. Die entsprechenden Effekte diese Items können aus dem desc feld des items gelesen werden.

### Schritt 6: races.json
- Hier muss traits in die traits.json ausgelagert werden und dann per indizes darauf verwisen werden. ein trait muss demnach auch um ein index feld und effect feld erweitert werden. Hier muss effect auch wieder durch indizes auf die effects.json verweisen.
- subraces gehört in die subraces.json ausgelagert. Die änderungen der traits von vorher muss auch hier angewandt werden.

