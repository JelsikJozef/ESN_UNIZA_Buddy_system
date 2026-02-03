# Univerzálny Export Priradení - Implementácia

## ✅ DOKONČENÉ

**Dátum:** 2026-02-03  
**Verzia:** 1.0

## Prehľad

Implementované **univerzálne riešenie** pre export manuálnych priradení, ktoré automaticky zahŕňa **VŠETKY stĺpce** z ESN a Erasmus datasetov, **okrem stĺpcov s odpoveďami na otázky**.

## Čo export obsahuje

### ✅ Automaticky zahrnuté stĺpce

Export **automaticky detekuje a zahŕňa VŠETKY stĺpce**, ktoré NIE SÚ v `question_columns`:

#### ESN stĺpce (s prefixom `ESN_`)
- Všetky stĺpce z ESN datasetu
- Napríklad: Name, Surname, Email, Phone, Facebook, Instagram, University, Faculty, Hobbies, Allergies, ...
- **Akékoľvek stĺpce**, ktoré sú v datasete a nie sú otázky

#### Erasmus stĺpce (s prefixom `Erasmus_`)
- Všetky stĺpce z Erasmus datasetu  
- Napríklad: Name, Surname, Email, WhatsApp, Telegram, Country, Arrival_Date, Departure_Date, Dietary_Restrictions, Allergies, Emergency_Contact, ...
- **Akékoľvek stĺpce**, ktoré sú v datasete a nie sú otázky

#### Dodatočné stĺpce
- **`Matching_Answers`** - Počet otázok, kde sa odpovede zhodujú
- **`Compared_Questions`** - Počet otázok, ktoré boli porovnané
- **`Assignment_Timestamp`** - Čas vytvorenia priradenia

### ❌ Automaticky vynechané stĺpce

- Všetky stĺpce, ktoré sú v `artifacts.question_columns`
- Teda všetky odpovede na otázky z formulárov

## Technická implementácia

### Kľúčový kód

```python
# Universal export with all columns
question_cols = set(question_columns) if question_columns else set()

# Add ESN columns - ALL columns except questions
for col in esn_df.columns:
    if col not in question_cols:
        col_name = f"ESN_{col}"
        value = esn_row[col]
        if pd.notna(value):
            row[col_name] = value

# Add Erasmus columns - ALL columns except questions
for col in erasmus_df.columns:
    if col not in question_cols:
        col_name = f"Erasmus_{col}"
        value = erasmus_row[col]
        if pd.notna(value):
            row[col_name] = value
```

### Logika

1. Vytvorí sa `set` z `question_columns` pre rýchle vyhľadávanie
2. Prejdú sa **všetky stĺpce** z ESN datasetu
3. Ak stĺpec **NIE JE** v `question_cols`, pridá sa do exportu s prefixom `ESN_`
4. To isté pre Erasmus dataset s prefixom `Erasmus_`
5. Prázdne hodnoty (NaN) sa vynechávajú

## Modifikované súbory

### 1. `src/view/export_assignments.py`

Funkcie `export_assignments_to_csv()` a `export_assignments_to_xlsx()` boli rozšírené:

**Nové parametre:**
```python
def export_assignments_to_csv(
    assignments: List[Assignment],
    esn_df: Optional[pd.DataFrame] = None,           # ← NOVÉ
    erasmus_df: Optional[pd.DataFrame] = None,       # ← NOVÉ
    question_columns: Optional[List[str]] = None,    # ← NOVÉ
    esn_vectors: Optional[np.ndarray] = None,        # ← NOVÉ
    erasmus_vectors: Optional[np.ndarray] = None     # ← NOVÉ
) -> bytes:
```

**Spätná kompatibilita:**
- Ak sa zavolá bez nových parametrov, funguje ako predtým (len základné údaje)
- Všetky staré testy prechádzajú ✅

### 2. `src/view/gui/app.py`

Funkcia `show_export_screen()` bola implementovaná:

**Funkcie:**
- Zobrazenie počtu priradení
- Export s plnými artifacts (všetky stĺpce)
- Informácia o tom, ktoré stĺpce budú exportované
- Preview tabuľka s počtom zhodných odpovedí

**Kľúčové volanie:**
```python
csv_bytes = export_assignments_to_csv(
    assignments,
    esn_df=artifacts.esn_df,
    erasmus_df=artifacts.erasmus_df,
    question_columns=artifacts.question_columns,
    esn_vectors=artifacts.esn_vectors,
    erasmus_vectors=artifacts.erasmus_vectors
)
```

## Testovanie

### Test: `test_universal_export.py`

Testuje export s rozsiahlymi datasetmi obsahujúcimi rôzne typy stĺpcov:

**ESN dataset (13 stĺpcov):**
- 10 non-question: Name, Surname, Email, Phone, Facebook, Instagram, University, Faculty, Hobbies, Allergies
- 3 question: Q1, Q2, Q3

**Erasmus dataset (15 stĺpcov):**
- 12 non-question: Name, Surname, Email, WhatsApp, Telegram, Home_University, Country, Arrival_Date, Departure_Date, Dietary_Restrictions, Allergies, Emergency_Contact
- 3 question: Q1, Q2, Q3

**Výsledok testu:**
```
✅ PASSED - 1 test
✓ CSV Export contains ALL non-question columns
✓ ESN columns exported: 10
✓ Erasmus columns exported: 12
✓ Questions excluded
✓ Matching count included
```

### Všetky export testy

```bash
pytest tests/ -k "export" -v
# Result: 9 passed ✅
```

## Príklad výstupu

### Excel export obsahuje:

| ESN_Name | ESN_Email | ESN_Phone | ESN_Allergies | Erasmus_Name | Erasmus_Email | Erasmus_WhatsApp | Erasmus_Country | Erasmus_Arrival_Date | Erasmus_Allergies | Matching_Answers | Compared_Questions |
|----------|-----------|-----------|---------------|--------------|---------------|------------------|-----------------|---------------------|-------------------|------------------|-------------------|
| John | john@esn.com | +421123456 | None | Alice | alice@mail.com | +34123456 | Spain | 2026-09-01 | Peanuts | 8 | 10 |
| Jane | jane@esn.com | +421654321 | Lactose | Bob | bob@mail.com | +34654321 | Spain | 2026-09-05 | None | 6 | 10 |

...a **všetky ďalšie stĺpce**, ktoré sú v datasetoch!

## Pre používateľov (ESNkári)

### Ako používať v GUI

1. Prejdite na **Export** obrazovku
2. V sekcii "Export Manual Assignments" uvidíte info o tom, koľko stĺpcov bude exportovaných
3. Kliknite na **"📥 Download Assignments as CSV"** alebo **"📊 Generate Assignments XLSX"**
4. Export obsahuje **automaticky všetky relevantné stĺpce**

### Čo nájdete v exporte

- ✅ **Kontaktné údaje** - email, telefón, sociálne siete
- ✅ **Dôležité info** - alergie, strava, dátumy príchodu
- ✅ **Univerzitné info** - škola, fakulta, krajina
- ✅ **Počet zhodných odpovedí** - indikátor kvality páru
- ✅ **A čokoľvek ďalšie**, čo je v datasete!
- ❌ **Bez** odpovedí na otázky (tie sú zbytočné v exporte)

## Výhody riešenia

### ✅ Univerzálne
- Funguje s **akýmikoľvek stĺpcami** v datasete
- Netreba upravovať kód pri pridaní nových stĺpcov
- Automatická detekcia question columns

### ✅ Flexibilné
- ESNkári vidia všetko, čo potrebujú
- Môžu si filtrovať/upravovať v Exceli
- Jeden súbor obsahuje všetko

### ✅ Spätne kompatibilné
- Staré volania fungujú bez zmeny
- Všetky existujúce testy prechádzajú
- Postupný prechod možný

### ✅ Prehľadné
- Prefíxy `ESN_` a `Erasmus_` jasne identifikujú zdroj
- Question columns automaticky vynechané
- Logické zoradenie stĺpcov

## Status

✅ **IMPLEMENTOVANÉ A OTESTOVANÉ**

- ✅ Univerzálny export všetkých stĺpcov
- ✅ Automatické filtrovanie question columns  
- ✅ Počet zhodných odpovedí
- ✅ GUI integrácia
- ✅ Spätná kompatibilita
- ✅ Testy (9/9 passed)
- ✅ Dokumentácia

---

**Pripravené na použitie! 🚀**
