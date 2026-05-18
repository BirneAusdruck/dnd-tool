1. Würfelbasierte Werte (betrifft ~77 Spells)
Jeder Schadenszauber: "1d8", "2d6+spellcasting_mod". Der Factory-_map_value() ignoriert aktuell alle String-Werte komplett. Selbst wenn man das fixen würde: Spells kombinieren meistens Würfel + Save + Condition in einem einzigen Effekt.

2. Saving Throw mit zwei Ausgängen (betrifft ~109 Spells)
Wir haben save_dc + save_stat jetzt im Schema – aber kein on_fail_effect / on_success_effect. Fireball: bei Fail vollen Schaden, bei Erfolg halben Schaden. Das braucht eine Verzweigung, keine einzelne Wirkung.

3. Level-Skalierung / Upcasting (betrifft ~45 Spells)
cure-wounds heilt 1d8 + spellcasting_mod auf Slot 1, 2d8 + mod auf Slot 2, etc. Es gibt kein upcast_scaling-Feld.

4. Zustände / Conditions auf Targets (betrifft ~42 Spells)
hold-person → paralyzed, charm-person → charmed, entangle → restrained. Kein applied_condition-Feld im Schema.

5. Flächeneffekte (AoE) (betrifft viele)
Fireball 20ft Sphere, Cone of Cold 60ft Cone, Lightning Bolt 100ft Line. Kein aoe_type / aoe_size-Feld.

6. Multi-Effekt-Spells (betrifft Großteil)
Haste: doppelte Speed + +2 AC + Advantage DEX saves + extra Action – das sind 4 gleichzeitige Effekte aus einer einzigen Spellwirkung.