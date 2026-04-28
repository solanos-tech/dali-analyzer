Rozumiem zakres. Przygotowałbym to jako **Markdown lookup dla dekodera**, ale od razu zaznaczę jedną rzecz: żeby to było naprawdę „kompletne” i bezpieczne implementacyjnie, warto zrobić to etapami i potem porównać z konkretną wersją normy IEC 62386-101/102/103, której używasz w projekcie. Poniżej daję Ci **szkielet i pierwszą wersję tabel lookup**, w formacie już nadającym się do dalszego utrzymywania.

Przyjmuję roboczo:

```text
IEC 62386-101 — warstwa systemowa / typy ramek / timing / forward/backward
IEC 62386-102 — control gear, czyli zasilacze, ballasty, LED drivers
IEC 62386-103 — control devices, czyli czujniki, przyciski, panele, kontrolery wejść
```

---

# DALI decoder lookup — IEC 62386-101/102/103

## 1. Typy ramek — IEC 62386-101

| Typ ramki          |                    Kierunek logiczny |     Liczba bitów danych | Przykład z logu             | Znaczenie dla dekodera                                |
| ------------------ | -----------------------------------: | ----------------------: | --------------------------- | ----------------------------------------------------- |
| Forward 16-bit     | master/control device → control gear |                      16 | `rx_forward16 raw=0xA900`   | Klasyczne komendy DALI do control gear, część 102     |
| Forward 24-bit     |    control device / controller → bus |                      24 | `rx_forward24 raw=0x01FE3C` | Komendy i eventy DALI-2 control devices, część 103    |
| Forward 32-bit     |                     controller → bus |                      32 | brak w logach               | Firmware/update/data transfer; poza bieżącym zakresem |
| Backward 8-bit     |                 odpowiedź urządzenia |                       8 | `rx_backward raw=0xFF`      | Odpowiedź na query/compare/verify                     |
| Corrupted backward |       odpowiedź kolizyjna/uszkodzona | niepoprawna ramka 8-bit | zależne od sniffera         | Może wystąpić, gdy kilka urządzeń odpowiada różnie    |

Backward frame **zawsze ma 8 bitów**, również w DALI-2. Różnica między DALI-1 i DALI-2 dotyczy głównie ramek forward, nie backward.

---

# 2. Forward 16-bit — struktura ogólna

Ramka:

```text
[ byte 0 ][ byte 1 ]
```

Bitowo:

```text
byte0: AAAAAA S / typ adresowania
byte1: command albo arc power level
```

## 2.1 Adresowanie w forward16

| Warunek / maska          |                                     Zakres `byte0` | Typ               | Dekodowanie bitów  | Znaczenie                          |
| ------------------------ | -------------------------------------------------: | ----------------- | ------------------ | ---------------------------------- |
| `(byte0 & 0x80) == 0x00` |                                        `0x00–0x7F` | Short address     | `AAAAAA S`         | Adres indywidualny control gear    |
| `(byte0 & 0xE0) == 0x80` |                                        `0x80–0x9F` | Group address     | `100 GGGG S`       | Adres grupowy 0–15                 |
| `byte0 == 0xFE`          |                                             `0xFE` | Broadcast DAPC    | —                  | Broadcast direct arc power         |
| `byte0 == 0xFF`          |                                             `0xFF` | Broadcast command | —                  | Broadcast command/query            |
| `byte0 in special range` | np. `0xA1`, `0xA3`, `0xA5`, `0xA7`, `0xA9`, `0xB1` | Special command   | zależne od komendy | Commissioning, DTR, search address |

### Bit `S`

| `S` | Znaczenie                                             |
| --: | ----------------------------------------------------- |
| `0` | Direct Arc Power Control, drugi bajt = poziom światła |
| `1` | Command / query, drugi bajt = opcode                  |

Przykłady:

```text
0x0191
byte0 = 0x01 = 00000001
short address = 0
S = 1
opcode = 0x91
```

```text
0xFE80
byte0 = 0xFE
broadcast DAPC
level = 0x80
```

```text
0xFF91
byte0 = 0xFF
broadcast command
opcode = 0x91
```

---

# 3. Forward 16-bit — Direct Arc Power Control

| Warunek             | Format                          | Znaczenie                                             | Backward | Send twice |
| ------------------- | ------------------------------- | ----------------------------------------------------- | -------- | ---------- |
| `S=0`               | `[address byte][level]`         | Ustawienie poziomu łuku/światła                       | Nie      | Nie        |
| `level = 0x00`      | OFF / minimum zależnie od stanu | Poziom 0                                              | Nie      | Nie        |
| `level = 0x01–0xFE` | poziom 1–254                    | Poziom jasności                                       | Nie      | Nie        |
| `level = 0xFF`      | MASK                            | Brak zmiany / wartość maskująca zależnie od kontekstu | Nie      | Nie        |

Przykład:

```text
0x0080
short address 0
DAPC level = 0x80
```

---

# 4. Forward 16-bit — komendy control gear, IEC 62386-102

## 4.1 Komendy sterujące poziomem

|      Opcode | Nazwa                   | Znaczenie                              | Backward | Send twice | Uwagi                |
| ----------: | ----------------------- | -------------------------------------- | -------- | ---------- | -------------------- |
|      `0x00` | OFF                     | Wyłączenie światła                     | Nie      | Nie        | Komenda adresowana   |
|      `0x01` | UP                      | Rozjaśnianie zgodnie z fade rate       | Nie      | Nie        | Iteracyjna           |
|      `0x02` | DOWN                    | Ściemnianie zgodnie z fade rate        | Nie      | Nie        | Iteracyjna           |
|      `0x03` | STEP UP                 | Krok w górę                            | Nie      | Nie        |                      |
|      `0x04` | STEP DOWN               | Krok w dół                             | Nie      | Nie        |                      |
|      `0x05` | RECALL MAX LEVEL        | Przejście do max level                 | Nie      | Nie        |                      |
|      `0x06` | RECALL MIN LEVEL        | Przejście do min level                 | Nie      | Nie        |                      |
|      `0x07` | STEP DOWN AND OFF       | Krok w dół; jeśli minimum, wyłącz      | Nie      | Nie        |                      |
|      `0x08` | ON AND STEP UP          | Włącz i krok w górę                    | Nie      | Nie        |                      |
|      `0x09` | ENABLE DAPC SEQUENCE    | Zezwala na sekwencję DAPC              | Nie      | Nie        | DALI-2               |
|      `0x0A` | GO TO LAST ACTIVE LEVEL | Powrót do ostatniego aktywnego poziomu | Nie      | Nie        | DALI-2               |
| `0x0B–0x0F` | Reserved                | Nie dekodować jako znana komenda       | —        | —          | Oznacz jako reserved |

---

## 4.2 Sceny

| Opcode / maska | Nazwa           | Parametr            | Backward | Send twice |
| -------------- | --------------- | ------------------- | -------- | ---------- |
| `0x10–0x1F`    | GO TO SCENE `n` | `n = opcode & 0x0F` | Nie      | Nie        |

Przykład:

```text
0x0114
short address 0
GO TO SCENE 4
```

---

## 4.3 Komendy konfigurujące

|      Opcode | Nazwa                      | Parametr                         | Backward | Send twice                      | Uwagi                        |
| ----------: | -------------------------- | -------------------------------- | -------- | ------------------------------- | ---------------------------- |
|      `0x20` | RESET                      | Reset parametrów control gear    | Nie      | Tak                             | Komenda zmienia konfigurację |
|      `0x21` | STORE ACTUAL LEVEL IN DTR0 | Zapis aktualnego poziomu do DTR0 | Nie      | Tak                             |                              |
|      `0x22` | SAVE PERSISTENT VARIABLES  | Wymuszenie zapisu trwałego       | Nie      | Tak                             | DALI-2                       |
|      `0x23` | SET OPERATING MODE         | Wartość z DTR0                   | Nie      | Tak                             |                              |
|      `0x24` | RESET MEMORY BANK          | Bank z DTR0                      | Nie      | Tak                             |                              |
|      `0x25` | IDENTIFY DEVICE            | Tryb identyfikacji urządzenia    | Nie      | Nie / zależnie od implementacji | DALI-2                       |
|      `0x26` | RESET POWER CYCLE SEEN     | Kasuje flagę power cycle seen    | Nie      | Tak                             | DALI-2                       |
| `0x27–0x29` | Reserved                   | —                                | —        | —                               |                              |

---

## 4.4 Store DTR0 as…

| Opcode | Nazwa                              | Parametr | Backward | Send twice |
| -----: | ---------------------------------- | -------- | -------- | ---------- |
| `0x2A` | STORE DTR0 AS MAX LEVEL            | `DTR0`   | Nie      | Tak        |
| `0x2B` | STORE DTR0 AS MIN LEVEL            | `DTR0`   | Nie      | Tak        |
| `0x2C` | STORE DTR0 AS SYSTEM FAILURE LEVEL | `DTR0`   | Nie      | Tak        |
| `0x2D` | STORE DTR0 AS POWER ON LEVEL       | `DTR0`   | Nie      | Tak        |
| `0x2E` | STORE DTR0 AS FADE TIME            | `DTR0`   | Nie      | Tak        |
| `0x2F` | STORE DTR0 AS FADE RATE            | `DTR0`   | Nie      | Tak        |

---

## 4.5 Store / remove / add scene and group

| Opcode / maska | Nazwa                   | Parametr            | Backward | Send twice |
| -------------- | ----------------------- | ------------------- | -------- | ---------- |
| `0x30–0x3F`    | STORE DTR0 AS SCENE `n` | `n = opcode & 0x0F` | Nie      | Tak        |
| `0x40–0x4F`    | REMOVE FROM SCENE `n`   | `n = opcode & 0x0F` | Nie      | Tak        |
| `0x50–0x5F`    | ADD TO GROUP `n`        | `n = opcode & 0x0F` | Nie      | Tak        |
| `0x60–0x6F`    | REMOVE FROM GROUP `n`   | `n = opcode & 0x0F` | Nie      | Tak        |

---

## 4.6 Short address / memory write

|      Opcode | Nazwa               | Parametr | Backward | Send twice | Uwagi                                  |
| ----------: | ------------------- | -------- | -------- | ---------- | -------------------------------------- |
|      `0x70` | SET SHORT ADDRESS   | `DTR0`   | Nie      | Tak        | `DTR0 = (short << 1) \| 1` albo `MASK` |
|      `0x71` | ENABLE WRITE MEMORY | —        | Nie      | Tak        | Zezwala na zapis memory bank           |
| `0x72–0x7F` | Reserved            | —        | —        | —          |                                        |

---

# 5. Forward 16-bit — query control gear

## 5.1 Query status i flagi

| Opcode | Nazwa                        | Backward         | Interpretacja odpowiedzi             |
| -----: | ---------------------------- | ---------------- | ------------------------------------ |
| `0x90` | QUERY STATUS                 | Byte statusu     | Odpowiedź bitowa, patrz tabela niżej |
| `0x91` | QUERY CONTROL GEAR PRESENT   | `0xFF` albo brak | `0xFF = YES`, brak = NO              |
| `0x92` | QUERY LAMP FAILURE           | `0xFF` albo brak | `YES/NO`                             |
| `0x93` | QUERY LAMP POWER ON          | `0xFF` albo brak | `YES/NO`                             |
| `0x94` | QUERY LIMIT ERROR            | `0xFF` albo brak | `YES/NO`                             |
| `0x95` | QUERY RESET STATE            | `0xFF` albo brak | `YES/NO`                             |
| `0x96` | QUERY MISSING SHORT ADDRESS  | `0xFF` albo brak | `YES/NO`                             |
| `0x97` | QUERY VERSION NUMBER         | Byte             | Numer wersji                         |
| `0x98` | QUERY CONTENT DTR0           | Byte             | Aktualny DTR0                        |
| `0x99` | QUERY DEVICE TYPE            | Byte             | Typ urządzenia                       |
| `0x9A` | QUERY PHYSICAL MINIMUM LEVEL | Byte             | Minimalny poziom fizyczny            |
| `0x9B` | QUERY POWER FAILURE          | `0xFF` albo brak | `YES/NO`                             |
| `0x9C` | QUERY CONTENT DTR1           | Byte             | Aktualny DTR1                        |
| `0x9D` | QUERY CONTENT DTR2           | Byte             | Aktualny DTR2                        |
| `0x9E` | QUERY OPERATING MODE         | Byte             | Tryb pracy                           |
| `0x9F` | QUERY LIGHT SOURCE TYPE      | Byte             | Typ źródła światła                   |

### QUERY STATUS — bity odpowiedzi

| Bit |  Maska | Znaczenie                  |
| --: | -----: | -------------------------- |
|   0 | `0x01` | Control gear failure       |
|   1 | `0x02` | Lamp failure               |
|   2 | `0x04` | Lamp power on              |
|   3 | `0x08` | Limit error                |
|   4 | `0x10` | Fade running / fade active |
|   5 | `0x20` | Reset state                |
|   6 | `0x40` | Missing short address      |
|   7 | `0x80` | Power failure seen         |

---

## 5.2 Query level/configuration values

|      Opcode | Nazwa                            | Backward                           | Interpretacja                   |
| ----------: | -------------------------------- | ---------------------------------- | ------------------------------- |
|      `0xA0` | QUERY ACTUAL LEVEL               | Byte                               | Aktualny poziom                 |
|      `0xA1` | QUERY MAX LEVEL                  | Byte                               | Max level                       |
|      `0xA2` | QUERY MIN LEVEL                  | Byte                               | Min level                       |
|      `0xA3` | QUERY POWER ON LEVEL             | Byte                               | Power-on level                  |
|      `0xA4` | QUERY SYSTEM FAILURE LEVEL       | Byte                               | System failure level            |
|      `0xA5` | QUERY FADE TIME / FADE RATE      | Byte                               | Nibble high/low                 |
|      `0xA6` | QUERY MANUFACTURER SPECIFIC MODE | Byte lub YES/NO zależnie od wersji | Do interpretacji kontekstowej   |
|      `0xA7` | QUERY NEXT DEVICE TYPE           | Byte                               | Kolejny obsługiwany device type |
|      `0xA8` | QUERY EXTENDED FADE TIME         | Byte                               | Encoded extended fade time      |
|      `0xA9` | QUERY CONTROL GEAR FAILURE       | `0xFF` albo brak                   | `YES/NO`                        |
| `0xAA–0xAF` | Reserved                         | —                                  | —                               |

### `QUERY FADE TIME / FADE RATE`

| Bity     | Znaczenie |
| -------- | --------- |
| `b7..b4` | fade time |
| `b3..b0` | fade rate |

---

## 5.3 Query scenes

| Opcode / maska | Nazwa                 |            Parametr | Backward               |
| -------------- | --------------------- | ------------------: | ---------------------- |
| `0xB0–0xBF`    | QUERY SCENE LEVEL `n` | `n = opcode & 0x0F` | Byte level albo `MASK` |

---

## 5.4 Query groups / random address / memory

|      Opcode | Nazwa                         | Backward                | Interpretacja                            |
| ----------: | ----------------------------- | ----------------------- | ---------------------------------------- |
|      `0xC0` | QUERY GROUPS 0–7              | Byte bitmapy            | Bity 0–7 = grupy 0–7                     |
|      `0xC1` | QUERY GROUPS 8–15             | Byte bitmapy            | Bity 0–7 = grupy 8–15                    |
|      `0xC2` | QUERY RANDOM ADDRESS H        | Byte                    | High byte random address                 |
|      `0xC3` | QUERY RANDOM ADDRESS M        | Byte                    | Middle byte random address               |
|      `0xC4` | QUERY RANDOM ADDRESS L        | Byte                    | Low byte random address                  |
|      `0xC5` | READ MEMORY LOCATION          | Byte                    | Odczyt banku/adresu wskazanego przez DTR |
| `0xC6–0xDF` | Reserved                      | —                       | —                                        |
| `0xE0–0xFF` | Application extended commands | zależnie od device type | Części 2xx, poza obecnym zakresem        |

Przykład z Twojego logu:

```text
0x01C2 → rx_backward 0x4E
0x01C3 → rx_backward 0x4C
0x01C4 → rx_backward 0xD3
```

Interpretacja:

```text
short address 0
QUERY RANDOM ADDRESS H/M/L
random address = 0x4E4CD3
```

---

# 6. Forward 16-bit — special commands / commissioning

Te komendy nie używają zwykłego pola adresu control gear. Są dekodowane po pierwszym bajcie.

| Raw pattern | Nazwa                 | Parametr | Backward                          | Send twice                      | Znaczenie                                        |
| ----------- | --------------------- | -------- | --------------------------------- | ------------------------------- | ------------------------------------------------ |
| `0xA100`    | TERMINATE             | —        | Nie                               | Nie                             | Kończy tryb inicjalizacji                        |
| `0xA3xx`    | SET DTR0              | `xx`     | Nie                               | Nie                             | Ustawia DTR0                                     |
| `0xA5xx`    | INITIALISE            | `xx`     | Nie                               | Tak                             | Wejście w tryb inicjalizacji                     |
| `0xA700`    | RANDOMISE             | —        | Nie                               | Tak                             | Generacja 24-bit random address                  |
| `0xA900`    | COMPARE               | —        | `0xFF` albo brak                  | Nie                             | `YES`, jeśli `random_address <= search_address`  |
| `0xAB00`    | WITHDRAW              | —        | Nie                               | Nie                             | Wycofuje znalezione urządzenie z dalszego search |
| `0xB1xx`    | SEARCHADDRH           | `xx`     | Nie                               | Nie                             | Ustawia high byte search address                 |
| `0xB3xx`    | SEARCHADDRM           | `xx`     | Nie                               | Nie                             | Ustawia middle byte search address               |
| `0xB5xx`    | SEARCHADDRL           | `xx`     | Nie                               | Nie                             | Ustawia low byte search address                  |
| `0xB7xx`    | PROGRAM SHORT ADDRESS | `xx`     | Nie                               | Nie                             | Programuje short address wybranego urządzenia    |
| `0xB9xx`    | VERIFY SHORT ADDRESS  | `xx`     | `0xFF` albo brak                  | Nie                             | Sprawdza short address                           |
| `0xBB00`    | QUERY SHORT ADDRESS   | —        | Byte albo brak                    | Zwraca zakodowany short address |                                                  |
| `0xBD00`    | PHYSICAL SELECTION    | —        | Nie                               | Nie                             | Wybór fizyczny urządzenia, jeśli obsługiwany     |
| `0xC1xx`    | ENABLE DEVICE TYPE    | `xx`     | Nie                               | Nie                             | Umożliwia komendy rozszerzone device type        |
| `0xC3xx`    | SET DTR1              | `xx`     | Nie                               | Nie                             | Ustawia DTR1                                     |
| `0xC5xx`    | SET DTR2              | `xx`     | Nie                               | Nie                             | Ustawia DTR2                                     |
| `0xC7xx`    | WRITE MEMORY LOCATION | `xx`     | Byte albo brak, zależnie od trybu | Nie / kontekstowo               | Zapis do memory bank                             |

Przykład z Twojego logu:

```text
0xB1FF
0xB3FF
0xB5FF
0xA900 → 0xFF
```

Interpretacja:

```text
SEARCHADDR = 0xFFFFFF
COMPARE = YES
```

---

# 7. Encoding short address

## 7.1 W adresowanym forward16

```text
byte0 = (short_address << 1) | S
```

| Pole            | Znaczenie     |
| --------------- | ------------- |
| `short_address` | `0–63`        |
| `S=0`           | DAPC          |
| `S=1`           | Command/query |

Przykład:

```text
short address 0, command:
(0 << 1) | 1 = 0x01
```

```text
0x0191 = short address 0, QUERY CONTROL GEAR PRESENT
```

---

## 7.2 W `PROGRAM SHORT ADDRESS`

```text
data = (short_address << 1) | 1
```

Przykład:

```text
short address 0 → data = 0x01
0xB701 = PROGRAM SHORT ADDRESS 0
```

---

# 8. Backward frame — interpretacja kontekstowa

Backward musi być interpretowany względem poprzedniej ramki forward.

| Poprzednia komenda     | Backward `0xFF`            | Brak backward   | Inny byte             |
| ---------------------- | -------------------------- | --------------- | --------------------- |
| `COMPARE`              | YES                        | NO              | nietypowe / corrupted |
| `QUERY ... YES/NO`     | YES                        | NO              | nietypowe             |
| `QUERY STATUS`         | status byte                | brak odpowiedzi | status byte           |
| `QUERY LEVEL`          | wartość 0–254 lub 255      | brak odpowiedzi | wartość               |
| `READ MEMORY LOCATION` | bajt danych                | brak odpowiedzi | bajt danych           |
| `QUERY SHORT ADDRESS`  | zakodowany adres albo MASK | brak odpowiedzi | bajt adresu           |
| `VERIFY SHORT ADDRESS` | YES                        | NO              | nietypowe             |

Dla dekodera ważne: `0xFF` nie zawsze znaczy tylko `YES`. Dla niektórych query może oznaczać też wartość `255` albo `MASK`.

---

# 9. Forward 24-bit — IEC 62386-103, control devices

Ramka:

```text
[ byte0 ][ byte1 ][ byte2 ]
```

Przykłady z Twojego logu:

```text
0xC10300
0x01FE3C
0x01018D
```

## 9.1 Klasy ramek forward24

| Warunek / wzorzec            | Klasa                                           | Znaczenie                                                 |
| ---------------------------- | ----------------------------------------------- | --------------------------------------------------------- |
| `byte0 == 0xC1`              | Special command / commissioning control devices | Wyszukiwanie i adresowanie urządzeń DALI-2 control device |
| `byte1 == 0xFE`              | Device-level command/query                      | Komendy do control device                                 |
| `byte1 != 0xFE`              | Instance/event related                          | Eventy albo komendy instancji                             |
| `byte0 == 0xFF`              | Broadcast control device command                | Broadcast do control devices                              |
| `byte0 == (short << 1) \| 1` | Short addressed control device command          | Komenda do control device o short address                 |

---

# 10. Forward 24-bit — commissioning control devices

Na podstawie IEC 62386-103 mechanizm jest analogiczny do control gear, ale używa 24-bitowych ramek.

| Raw pattern | Nazwa                 | Parametr | Backward         | Send twice | Znaczenie                                       |
| ----------- | --------------------- | -------- | ---------------- | ---------- | ----------------------------------------------- |
| `0xC10000`  | TERMINATE             | —        | Nie              | Nie        | Koniec trybu inicjalizacji control devices      |
| `0xC101xx`  | INITIALISE            | `xx`     | Nie              | Tak        | Wejście w tryb inicjalizacji control devices    |
| `0xC10200`  | RANDOMISE             | —        | Nie              | Tak        | Generacja random address                        |
| `0xC10300`  | COMPARE               | —        | `0xFF` albo brak | Nie        | `YES`, jeśli `random_address <= search_address` |
| `0xC10400`  | WITHDRAW              | —        | Nie              | Nie        | Wycofuje znalezione urządzenie                  |
| `0xC105xx`  | SEARCHADDRH           | `xx`     | Nie              | Nie        | High byte search address                        |
| `0xC106xx`  | SEARCHADDRM           | `xx`     | Nie              | Nie        | Middle byte search address                      |
| `0xC107xx`  | SEARCHADDRL           | `xx`     | Nie              | Nie        | Low byte search address                         |
| `0xC108xx`  | PROGRAM SHORT ADDRESS | `xx`     | Nie              | Nie        | Programowanie short address control device      |
| `0xC109xx`  | VERIFY SHORT ADDRESS  | `xx`     | `0xFF` albo brak | Nie        | Weryfikacja short address                       |
| `0xC10A00`  | QUERY SHORT ADDRESS   | —        | Byte albo brak   | Nie        | Odczyt short address                            |

Przykład z Twojego logu:

```text
0xC105FF
0xC106FF
0xC107FF
0xC10300 → 0xFF
```

Interpretacja:

```text
SEARCHADDR = 0xFFFFFF
COMPARE = YES
```

---

# 11. Forward 24-bit — DTR / memory helpers dla control devices

| Raw pattern | Nazwa robocza                  | Parametr | Backward            | Uwagi                                       |
| ----------- | ------------------------------ | -------- | ------------------- | ------------------------------------------- |
| `0xC130xx`  | SET DTR0 / data register 0     | `xx`     | Nie                 | Używane przed odczytem/zapisem memory       |
| `0xC131xx`  | SET DTR1 / data register 1     | `xx`     | Nie                 | Używane jako bank/index zależnie od komendy |
| `0xC132xx`  | SET DTR2 / data register 2     | `xx`     | Nie                 | Do potwierdzenia w implementacji            |
| `0xC9xxxx`  | WRITE / memory-related command | `xxxx`   | zależnie od komendy | Do walidacji z tabelą 103                   |

W Twoich logach:

```text
0xC13100
0xC1308F
0x01FE3C
```

wygląda jak ustawienie wskaźników pamięci i późniejszy odczyt kolejnych bajtów przez `0x01FE3C`.

---

# 12. Forward 24-bit — device-level commands / queries

Wzorzec:

```text
[ address byte ][ 0xFE ][ opcode ]
```

Przykład:

```text
0x01FE30
```

Dekodowanie:

```text
byte0 = 0x01 → short address 0, command
byte1 = 0xFE → device-level command/query
byte2 = 0x30 → opcode
```

## 12.1 Device-level query lookup — core

| Pattern    | Nazwa                                               | Backward | Znaczenie                                                     |
| ---------- | --------------------------------------------------- | -------- | ------------------------------------------------------------- |
| `xx FE 30` | QUERY CONTROL DEVICE STATUS / PRESENT / core status | Byte     | Status lub identyfikacja obecności — zależnie od opcode w 103 |
| `xx FE 39` | QUERY IDENTIFICATION / RANDOM / memory-related H    | Byte     | W Twoim logu zwraca byte danych                               |
| `xx FE 3A` | QUERY IDENTIFICATION / RANDOM / memory-related M    | Byte     | W Twoim logu zwraca byte danych                               |
| `xx FE 3B` | QUERY IDENTIFICATION / RANDOM / memory-related L    | Byte     | W Twoim logu zwraca byte danych                               |
| `xx FE 3C` | READ MEMORY LOCATION                                | Byte     | Odczyt kolejnego bajtu z memory bank                          |

Przykład z Twojego logu:

```text
0x01FE3C → 0x4C
0x01FE3C → 0x75
0x01FE3C → 0x6E
0x01FE3C → 0x61
```

ASCII:

```text
4C 75 6E 61 = "Luna"
```

---

# 13. Forward 24-bit — event / input notification

Wzorzec ogólny:

```text
[ source/address ][ instance ][ event ]
```

Przykłady:

```text
0x01018C
0x01018D
```

Dekodowanie robocze:

```text
byte0 = 0x01 → short address 0 / source device
byte1 = 0x01 → instance 1
byte2 = 0x8C / 0x8D → event code
```

| Pole              | Znaczenie                                 |                                      |
| ----------------- | ----------------------------------------- | ------------------------------------ |
| `byte0`           | adres control device / źródło eventu      |                                      |
| `byte1`           | numer instancji                           |                                      |
| `byte2`           | kod eventu                                |                                      |
| `byte2 0x80–0xBF` | typowy zakres eventów/input notifications |                                      |
| Backward          | Nie                                       | Event nie wymaga odpowiedzi backward |

Dla dekodera:

```text
jeśli frame24 nie ma byte1 == 0xFE i nie jest special C1xxxx,
traktuj jako event/instance-related frame
```

---

# 14. Send twice — reguły do dekodera

| Klasa komendy                | Send twice |
| ---------------------------- | ---------- |
| DAPC                         | Nie        |
| Komendy sterujące poziomem   | Zwykle nie |
| Query                        | Nie        |
| `RESET`, store/configuration | Tak        |
| `INITIALISE`                 | Tak        |
| `RANDOMISE`                  | Tak        |
| `SEARCHADDRH/M/L`            | Nie        |
| `COMPARE`                    | Nie        |
| `PROGRAM SHORT ADDRESS`      | Nie        |
| `VERIFY SHORT ADDRESS`       | Nie        |
| `WITHDRAW`                   | Nie        |
| `ENABLE WRITE MEMORY`        | Tak        |
| `SAVE PERSISTENT VARIABLES`  | Tak        |

Dla sniffera/dekodera dobrze mieć osobną flagę:

```text
send_twice_expected = true/false
```

i ostrzeżenie:

```text
expected repeated frame not observed within timing window
```

---

# 15. Przykładowe reguły klasyfikacji dla dekodera

## 15.1 Forward16

```text
if frame_len == 16:
    byte0 = raw >> 8
    byte1 = raw & 0xFF

    if byte0 in special_command_table:
        decode as special command

    else if byte0 == 0xFE:
        decode as broadcast DAPC

    else if byte0 == 0xFF:
        decode as broadcast command/query

    else if (byte0 & 0x80) == 0:
        short = byte0 >> 1
        selector = byte0 & 1

        if selector == 0:
            decode byte1 as arc power level
        else:
            decode byte1 as control gear opcode

    else if (byte0 & 0xE0) == 0x80:
        group = (byte0 >> 1) & 0x0F
        selector = byte0 & 1
```

---

## 15.2 Forward24

```text
if frame_len == 24:
    b0 = raw >> 16
    b1 = (raw >> 8) & 0xFF
    b2 = raw & 0xFF

    if b0 == 0xC1:
        decode as control-device special/commissioning command

    else if b1 == 0xFE:
        decode as control-device device-level command/query

    else:
        decode as input notification / instance event / instance command
```

---

# 16. Minimalny model backward context

Dekoder powinien pamiętać ostatnią ramkę forward, która mogła wywołać backward.

| Pole kontekstu       | Przykład                                                        |
| -------------------- | --------------------------------------------------------------- |
| `last_forward_type`  | `forward16`, `forward24`                                        |
| `last_command`       | `COMPARE`, `QUERY STATUS`, `READ MEMORY LOCATION`               |
| `expects_backward`   | `true/false`                                                    |
| `backward_mode`      | `YES_NO`, `BYTE`, `STATUS_BYTE`, `MEMORY_BYTE`, `SHORT_ADDRESS` |
| `expected_window_ms` | okno odpowiedzi backward                                        |
| `actual_backward`    | `0xFF`, `0x00`, `0x4C`, brak                                    |

Przykład:

```text
rx_forward16 0xA900
rx_backward  0xFF
```

Dekoder:

```text
command = COMPARE
backward_mode = YES_NO
result = YES
```

Przykład:

```text
rx_forward24 0x01FE3C
rx_backward  0x4C
```

Dekoder:

```text
command = READ MEMORY LOCATION
backward_mode = MEMORY_BYTE
result = 0x4C
ascii = 'L'
```

---

# 17. Status implementacyjny tej tabeli

Do dekodera od razu bezpiecznie można wziąć:

```text
- klasyfikację ramek 16/24/8 bit,
- adresowanie forward16,
- DAPC,
- komendy 102 od 0x00 do 0xC5,
- special commands 16-bit,
- commissioning DALI-1,
- commissioning DALI-2 control devices,
- kontekstową interpretację backward,
- READ MEMORY LOCATION z ASCII/debug output.
```



Tak — przygotuję to, ale muszę rozdzielić jedną ważną rzecz:

**IEC 62386-103** opisuje wspólny mechanizm dla control devices: adresowanie, ramki 24-bit, komendy device-level, instancje, memory access, event routing itd.

Natomiast **pełne eventy instancji** są rozproszone po częściach **IEC 62386-3xx**, np. przyciski, sensory obecności, czujniki światła itd. Nie ma jednej uniwersalnej tabeli eventów dla wszystkich instancji tylko w 103. Dlatego najlepszy model dekodera to:

```text
forward24
 ├─ control-device special commands
 ├─ device-level commands: xx FE yy
 ├─ instance commands: xx ii yy
 └─ input notifications/events: xx ii ee
        └─ interpretacja zależna od instance_type z części 3xx
```

Poniżej masz pierwszą część lookupu: **pełne rozdzielenie typów ramek 24-bit, device-level core dla 103, model eventów/instancji i dispatch pod 3xx**.

---

# DALI-2 / IEC 62386-103 — lookup dla ramek 24-bit

## 1. Podstawowa klasyfikacja forward24

Ramka 24-bit:

```text
raw = 0xAABBCC

byte0 = AA
byte1 = BB
byte2 = CC
```

Standardowo:

```text
[ byte0 ][ byte1 ][ byte2 ]
[ addr  ][ target/opcode group ][ opcode/event/data ]
```

W DALI ramka forward może mieć 16, 24 lub 32 bity danych, a backward frame ma 8 bitów danych. 

---

## 2. Główne klasy ramek 24-bit

| Warunek                                          | Klasa                                           | Przykład   | Znaczenie                                                           |
| ------------------------------------------------ | ----------------------------------------------- | ---------- | ------------------------------------------------------------------- |
| `byte0 == 0xC1`                                  | Special command / commissioning control devices | `0xC10300` | Wyszukiwanie, randomise, compare, short address dla control devices |
| `byte1 == 0xFE`                                  | Device-level command/query                      | `0x01FE30` | Komenda do całego control device                                    |
| `byte1 != 0xFE` i ramka pochodzi od kontrolera   | Instance command                                | `0x0101xx` | Komenda do konkretnej instancji                                     |
| `byte1 != 0xFE` i ramka pochodzi od input device | Event / input notification                      | `0x01018D` | Zdarzenie z instancji, np. przycisk/sensor                          |
| `byte0 == 0xFF` i `byte1 == 0xFE`                | Broadcast device-level                          | `0xFFFE1D` | Broadcast do wszystkich control devices                             |
| `byte0 == 0xFF` i `byte1 != 0xFE`                | Broadcast / special instance-related            | `0xFF01xx` | Zależne od kontekstu                                                |
| `byte0 == 0xC9`                                  | Special / memory / extended helper              | `0xC9FFFF` | Wymaga osobnej obsługi jako special 103                             |
| inne `0xC?xxxx`                                  | Special command space                           | `0xC1308F` | DTR / konfiguracja / helper                                         |

---

# 3. Adresowanie control device w forward24

## 3.1 Short address encoding

Dla adresu krótkiego control device:

```text
byte0 = (short_address << 1) | 1
```

| Short address | `byte0` |
| ------------: | ------: |
|           `0` |  `0x01` |
|           `1` |  `0x03` |
|           `2` |  `0x05` |
|           `3` |  `0x07` |
|          `63` |  `0x7F` |

Przykład:

```text
0x01FE30
```

Dekodowanie:

```text
byte0 = 0x01 → short address 0
byte1 = 0xFE → device-level command
byte2 = 0x30 → opcode 0x30
```

---

## 3.2 Broadcast

|                 `byte0` | Znaczenie                                                                           |
| ----------------------: | ----------------------------------------------------------------------------------- |
|                  `0xFF` | Broadcast do control devices                                                        |
| `0xFD` / inne specjalne | Zależne od adresowania grupowego/specjalnego — do osobnej tabeli po walidacji z 103 |

Przykład z logu:

```text
0xFFFE1D
```

Dekodowanie:

```text
byte0 = 0xFF → broadcast
byte1 = 0xFE → device-level
byte2 = 0x1D → opcode 0x1D
```

---

# 4. Special commands control devices — commissioning

Te komendy są odpowiednikiem klasycznego commissioning dla control gear, ale dla control devices i w ramkach 24-bit.

| Raw pattern | Komenda               | Parametr | Backward         | Send twice | Znaczenie                                     |
| ----------- | --------------------- | -------: | ---------------- | ---------- | --------------------------------------------- |
| `0xC10000`  | TERMINATE             |        — | Nie              | Nie        | Zakończenie trybu initialisation              |
| `0xC101xx`  | INITIALISE            |     `xx` | Nie              | Tak        | Wejście w tryb initialisation                 |
| `0xC10200`  | RANDOMISE             |        — | Nie              | Tak        | Wygenerowanie random address                  |
| `0xC10300`  | COMPARE               |        — | `0xFF` albo brak | Nie        | YES, jeśli `random_address <= search_address` |
| `0xC10400`  | WITHDRAW              |        — | Nie              | Nie        | Wycofanie aktualnie znalezionego urządzenia   |
| `0xC105xx`  | SEARCHADDRH           |     `xx` | Nie              | Nie        | High byte search address                      |
| `0xC106xx`  | SEARCHADDRM           |     `xx` | Nie              | Nie        | Middle byte search address                    |
| `0xC107xx`  | SEARCHADDRL           |     `xx` | Nie              | Nie        | Low byte search address                       |
| `0xC108xx`  | PROGRAM SHORT ADDRESS |     `xx` | Nie              | Nie        | Programuje short address control device       |
| `0xC109xx`  | VERIFY SHORT ADDRESS  |     `xx` | `0xFF` albo brak | Nie        | Weryfikuje short address                      |
| `0xC10A00`  | QUERY SHORT ADDRESS   |        — | Byte albo brak   | Nie        | Odczyt short address                          |

Przykład:

```text
0xC105FF
0xC106FF
0xC107FF
0xC10300 → rx_backward 0xFF
```

Interpretacja:

```text
SEARCHADDR = 0xFFFFFF
COMPARE = YES
```

---

# 5. Special helper commands — DTR / memory context

W logach widać typowe komendy pomocnicze używane przed odczytem pamięci.

| Raw pattern | Nazwa robocza           | Parametr | Backward            | Znaczenie                        |
| ----------- | ----------------------- | -------: | ------------------- | -------------------------------- |
| `0xC130xx`  | SET DTR0                |     `xx` | Nie                 | Ustawia DTR0 dla control devices |
| `0xC131xx`  | SET DTR1                |     `xx` | Nie                 | Ustawia DTR1                     |
| `0xC132xx`  | SET DTR2                |     `xx` | Nie                 | Ustawia DTR2                     |
| `0xC9xxxx`  | Extended/special helper |   `xxxx` | Zależnie od komendy | Do walidacji z tabelą 103        |

Przykład z logu:

```text
0xC13100
0xC1308F
0x01FE3C
```

Interpretacja praktyczna:

```text
DTR1 = 0x00
DTR0 = 0x8F
READ MEMORY LOCATION
```

---

# 6. Device-level commands: `xx FE yy`

Format:

```text
[ address ][ 0xFE ][ opcode ]
```

Przykład:

```text
0x01FE30
```

Dekodowanie:

```text
address = 0x01 → short address 0
target  = 0xFE → device-level
opcode  = 0x30
```

---

## 6.1 Device-level opcode table — IEC 62386-103 core

Poniżej tabela w układzie implementacyjnym. Kolumny `Backward mode` i `Send twice` są najważniejsze dla dekodera.

|      Opcode | Nazwa / rola                                 | Typ                   | Backward mode             | Send twice     | Uwagi dekodera                                   |
| ----------: | -------------------------------------------- | --------------------- | ------------------------- | -------------- | ------------------------------------------------ |
|      `0x00` | RESET                                        | Instruction           | Brak                      | Tak            | Resetuje control device / parametry device-level |
|      `0x01` | IDENTIFY DEVICE                              | Instruction           | Brak                      | Nie            | Tryb identyfikacji fizycznej                     |
|      `0x02` | RESET POWER CYCLE SEEN                       | Instruction           | Brak                      | Tak            | Kasuje flagę power-cycle                         |
| `0x03–0x0F` | Reserved / not implemented                   | —                     | —                         | —              | Pokazać jako reserved                            |
|      `0x10` | SET SHORT ADDRESS / device config command    | Instruction           | Brak                      | Tak / kontekst | Uwaga: dokładne znaczenie zależne od tabeli 103  |
|      `0x11` | ENABLE APPLICATION CONTROLLER / config       | Instruction           | Brak                      | Tak / kontekst | Do walidacji z 103                               |
|      `0x12` | DISABLE APPLICATION CONTROLLER / config      | Instruction           | Brak                      | Tak / kontekst | Do walidacji z 103                               |
|      `0x13` | SET OPERATING MODE / config                  | Instruction           | Brak                      | Tak            | Wartość zwykle z DTR0                            |
|      `0x14` | SET EVENT PRIORITY / event config            | Instruction           | Brak                      | Tak            | W logu: `0xFFFE14` po `C130FF`                   |
|      `0x15` | ENABLE INSTANCE / instance config            | Instruction           | Brak                      | Tak            | Do walidacji z 103                               |
|      `0x16` | DISABLE INSTANCE / instance config           | Instruction           | Brak                      | Tak            | Do walidacji z 103                               |
|      `0x17` | SET PRIMARY INSTANCE GROUP                   | Instruction           | Brak                      | Tak            | Wartość z DTR0                                   |
|      `0x18` | SET INSTANCE GROUP 1                         | Instruction           | Brak                      | Tak            | Wartość z DTR0                                   |
|      `0x19` | SET INSTANCE GROUP 2                         | Instruction           | Brak                      | Tak            | Wartość z DTR0                                   |
|      `0x1A` | SET EVENT SCHEME                             | Instruction           | Brak                      | Tak            | Wartość z DTR0                                   |
|      `0x1B` | SET EVENT FILTER                             | Instruction           | Brak                      | Tak            | W logu: `0xFFFE1B`                               |
|      `0x1C` | RESET EVENT FILTER / set event config        | Instruction           | Brak                      | Tak            | W logu: `0xFFFE1C`                               |
|      `0x1D` | ENABLE DEVICE / ENABLE EVENTS / config       | Instruction           | Brak                      | Tak            | W logu: `0xFFFE1D`                               |
|      `0x1E` | DISABLE DEVICE / DISABLE EVENTS / config     | Instruction           | Brak                      | Tak            | W logu: `0xFFFE1E`                               |
|      `0x1F` | Reserved / implementation-specific           | —                     | —                         | —              | Sprawdzić w 103                                  |
| `0x20–0x2F` | Configuration instructions                   | Instruction           | Brak / zależnie od opcode | Zwykle Tak     | Zakres do uzupełnienia z tabeli 103              |
|      `0x30` | QUERY CONTROL DEVICE STATUS                  | Query                 | Status byte               | Nie            | W logu: `0x01FE30 → 0x22`                        |
|      `0x31` | QUERY DEVICE GROUPS 0–7 / config state       | Query                 | Byte bitmap               | Nie            | Do walidacji z 103                               |
|      `0x32` | QUERY DEVICE GROUPS 8–15 / config state      | Query                 | Byte bitmap               | Nie            | Do walidacji z 103                               |
|      `0x33` | QUERY OPERATING MODE                         | Query                 | Byte                      | Nie            |                                                  |
|      `0x34` | QUERY MANUFACTURER SPECIFIC MODE / state     | Query                 | Byte                      | Nie            |                                                  |
|      `0x35` | QUERY VERSION NUMBER                         | Query                 | Byte                      | Nie            |                                                  |
|      `0x36` | QUERY NUMBER OF INSTANCES                    | Query                 | Byte                      | Nie            |                                                  |
|      `0x37` | QUERY CONTENT DTR0                           | Query                 | Byte                      | Nie            |                                                  |
|      `0x38` | QUERY CONTENT DTR1 / DTR2                    | Query                 | Byte                      | Nie            | Do walidacji                                     |
|      `0x39` | QUERY RANDOM ADDRESS H                       | Query                 | Byte                      | Nie            | W logu: `0x01FE39 → 0x2B`                        |
|      `0x3A` | QUERY RANDOM ADDRESS M                       | Query                 | Byte                      | Nie            | W logu: `0x01FE3A → 0xF4`                        |
|      `0x3B` | QUERY RANDOM ADDRESS L                       | Query                 | Byte                      | Nie            | W logu: `0x01FE3B → 0xF6`                        |
|      `0x3C` | READ MEMORY LOCATION                         | Query                 | Memory byte               | Nie            | W logu: `0x01FE3C → ASCII/data`                  |
| `0x3D–0x7F` | Reserved / 103-specific query space          | —                     | —                         | —              | Nie zgadywać nazwy bez tabeli 103                |
| `0x80–0xFF` | Extended / instance-type / application space | Zależnie od kontekstu | Zależnie od komendy       | Zależnie       | Dispatch do 3xx lub extension                    |

### Uwaga implementacyjna

Dla opcode `0x10–0x2F` i części `0x31–0x38` zostawiłem opisy jako **konserwatywne**, bo nazwy muszą zostać zweryfikowane linia po linii z konkretną wersją IEC 62386-103, żeby nie wprowadzić błędnych nazw w dekoderze. Natomiast klasyfikacja typu `instruction/query`, obecność backward i rola zakresu są poprawne dla logiki dekodera.

---

# 7. `QUERY CONTROL DEVICE STATUS` — `xx FE 30`

Format:

```text
xx FE 30
```

Przykład:

```text
0x01FE30 → rx_backward 0x22
```

Tabela bitowa odpowiedzi — model dekodera:

| Bit |  Maska | Znaczenie robocze                           |
| --: | -----: | ------------------------------------------- |
|   0 | `0x01` | input device error / device failure         |
|   1 | `0x02` | power cycle seen                            |
|   2 | `0x04` | reset state                                 |
|   3 | `0x08` | missing short address                       |
|   4 | `0x10` | application controller error / device state |
|   5 | `0x20` | instance-related status / device active     |
|   6 | `0x40` | reserved / implementation-specific          |
|   7 | `0x80` | reserved / implementation-specific          |

Dla dekodera na razie bezpiecznie:

```text
0x01FE30 → status byte
nie traktować 0xFF wyłącznie jako YES
```

---

# 8. `READ MEMORY LOCATION` — `xx FE 3C`

Format:

```text
xx FE 3C
```

Wymaga ustawienia wskaźnika pamięci przez DTR:

```text
C131bb → bank / DTR1
C130aa → address / DTR0
xxFE3C → read memory location
```

Przykład z logu:

```text
C13100
C1308F
01FE3C → 0x05
01FE3C → 0x27
01FE3C → 0x3D
01FE3C → 0xBA
01FE3C → 0x2D
01FE3C → 0x49
01FE3C → 0x4E
01FE3C → 0x54
...
```

ASCII fragment:

```text
2D 49 4E 54 2D 41 51 2D 4C 45 2D 57 31 36
= "-INT-AQ-LE-W16"
```

Dla dekodera:

| Warunek                     | Interpretacja                                                 |
| --------------------------- | ------------------------------------------------------------- |
| Poprzednia komenda `xxFE3C` | backward = bajt danych                                        |
| Byte `0x20–0x7E`            | opcjonalnie pokaż ASCII                                       |
| Byte `0x00`                 | terminator / padding / wartość danych zależnie od memory bank |
| Brak backward               | brak danych / urządzenie nie odpowiada / invalid address      |

---

# 9. Instance commands: `xx ii yy`

Format:

```text
[ address ][ instance ][ opcode ]
```

Przykład abstrakcyjny:

```text
0x01018C
```

Dekodowanie:

```text
address  = 0x01 → short address 0
instance = 0x01
opcode/event = 0x8C
```

## 9.1 Jak odróżnić instance command od eventu

To jest kluczowe dla sniffera.

| Kryterium             | Instance command             | Event / input notification       |
| --------------------- | ---------------------------- | -------------------------------- |
| Kto nadaje            | application controller       | input device                     |
| Czy oczekuje backward | czasami tak                  | nie                              |
| `byte1`               | numer instancji              | numer instancji                  |
| `byte2`               | opcode komendy do instancji  | event information                |
| Timing                | zwykle po stronie kontrolera | może pojawić się asynchronicznie |
| Przykład              | `controller → 0x0101xx`      | `sensor → 0x01018D`              |

Jeżeli sniffer nie zna fizycznego kierunku nadawcy, stosuj heurystykę:

```text
jeśli byte1 != 0xFE
i byte2 mieści się w zakresie eventów
i po ramce nie występuje backward
i ramka pojawia się asynchronicznie,
to klasyfikuj jako input notification / event.
```

---

# 10. Event / input notification — model ogólny 103

Format ogólny:

```text
[ source address ][ instance ][ event information ]
```

| Pole                 | Znaczenie                               |
| -------------------- | --------------------------------------- |
| `byte0`              | adres źródłowego control device         |
| `byte1`              | numer instancji                         |
| `byte2`              | event information / event code          |
| Backward             | Nie występuje                           |
| Interpretacja eventu | zależna od `instance_type` z części 3xx |

Przykład z Twoich wcześniejszych logów:

```text
0x01018C
0x01018D
```

Dekoder powinien pokazać:

```text
device short address: 0
instance: 1
event information: 0x8C / 0x8D
type: input notification / event
backward expected: no
```

---

# 11. Dispatch eventów według instance type — 3xx

Najbezpieczniejszy model dekodera:

```text
1. Odczytaj liczbę instancji.
2. Dla każdej instancji odczytaj instance type.
3. Dla eventów xx ii ee:
   - znajdź device address
   - znajdź instance ii
   - znajdź instance_type
   - interpretuj ee według właściwej tabeli 3xx
```

## 11.1 Główna tabela dispatch

| Instance type | Część IEC     | Typ instancji                | Jak dekodować event                    |
| ------------: | ------------- | ---------------------------- | -------------------------------------- |
|        `0x01` | IEC 62386-301 | Push button / input switch   | Eventy przycisku                       |
|        `0x02` | IEC 62386-302 | Absolute input               | Wartość absolutna / poziom             |
|        `0x03` | IEC 62386-303 | Occupancy sensor             | Zdarzenia obecności                    |
|        `0x04` | IEC 62386-304 | Light sensor                 | Zdarzenia / wartości natężenia światła |
|        `0x05` | IEC 62386-305 | Colour sensor                | Zdarzenia / wartości barwowe           |
|        `0x06` | IEC 62386-306 | General purpose sensor       | Zdarzenia sensora ogólnego             |
|        `0x07` | IEC 62386-307 | Thermal sensor / temperature | Zdarzenia/wartości temperaturowe       |
|       `0x08+` | kolejne 3xx   | Inne typy                    | Wymaga tabeli właściwej części         |

---

# 12. Event schemes

W 103 event może być kodowany według różnych schematów. Dlatego samo `0x8C` nie zawsze wystarczy bez znajomości konfiguracji event scheme.

Dla dekodera trzymaj przy instancji:

```text
instance_type
event_scheme
event_filter
event_priority
instance_group
```

## 12.1 Ogólny model event scheme

| Event scheme               | Co zawiera event                         | Konsekwencja dla dekodera              |
| -------------------------- | ---------------------------------------- | -------------------------------------- |
| Device/instance addressing | Device address + instance number + event | Najłatwiejsze do dekodowania           |
| Device group addressing    | Device group + instance + event          | Potrzebna mapa grup                    |
| Instance group addressing  | Instance group + event                   | Potrzebna konfiguracja instance groups |
| Broadcast event            | Event bez jednoznacznego device/instance | Traktować ostrożnie                    |

---

# 13. IEC 62386-301 — Push button instance events

Poniżej tabela robocza dla przycisków. Wartość eventu należy interpretować przez `instance_type = 0x01`.

|  Event code | Nazwa eventu                     | Znaczenie                           | Backward |
| ----------: | -------------------------------- | ----------------------------------- | -------- |
|      `0x00` | Button released                  | Przycisk zwolniony                  | Nie      |
|      `0x01` | Button pressed                   | Przycisk naciśnięty                 | Nie      |
|      `0x02` | Short press                      | Krótkie naciśnięcie                 | Nie      |
|      `0x03` | Double press                     | Podwójne naciśnięcie                | Nie      |
|      `0x04` | Long press start                 | Początek długiego naciśnięcia       | Nie      |
|      `0x05` | Long press repeat                | Powtarzanie długiego naciśnięcia    | Nie      |
|      `0x06` | Long press stop                  | Koniec długiego naciśnięcia         | Nie      |
|      `0x07` | Button free                      | Przycisk zwolniony z blokady / free | Nie      |
|      `0x08` | Button stuck                     | Przycisk zablokowany                | Nie      |
| `0x09–0x7F` | Reserved / vendor-specific       | Nieznane                            | Nie      |
| `0x80–0xFF` | Encoded event / scheme-dependent | Zależne od event scheme             | Nie      |

---

# 14. IEC 62386-302 — Absolute input events

Absolute input zwykle przenosi wartość liczbową, a nie prosty enum jak przycisk.

| Event information | Znaczenie                                   | Backward | Uwagi                                       |
| ----------------: | ------------------------------------------- | -------- | ------------------------------------------- |
|       `0x00–0xFE` | Encoded absolute value                      | Nie      | Wartość zależna od rozdzielczości instancji |
|            `0xFF` | MASK / invalid / no value                   | Nie      | Kontekstowo                                 |
|  scheme-dependent | Event z wartością wielobajtową / filtrowaną | Nie      | Wymaga konfiguracji instancji               |

Dla dekodera:

```text
instance_type = 0x02
event = absolute_input_event
value_raw = event_information
```

---

# 15. IEC 62386-303 — Occupancy sensor events

|  Event code | Nazwa robocza                  | Znaczenie               | Backward |
| ----------: | ------------------------------ | ----------------------- | -------- |
|      `0x00` | No movement / vacant           | Brak obecności/ruchu    | Nie      |
|      `0x01` | Movement / occupied            | Wykryto obecność/ruch   | Nie      |
|      `0x02` | Still vacant                   | Nadal brak obecności    | Nie      |
|      `0x03` | Still occupied                 | Nadal obecność          | Nie      |
| `0x04–0x7F` | Reserved / sensor-specific     | Do walidacji z 303      | Nie      |
| `0x80–0xFF` | Scheme-dependent encoded event | Zależne od event scheme | Nie      |

---

# 16. IEC 62386-304 — Light sensor events

| Event information | Znaczenie                         | Backward | Uwagi                                 |
| ----------------: | --------------------------------- | -------- | ------------------------------------- |
|       `0x00–0xFE` | Encoded illuminance / light level | Nie      | Wymaga skali/rozdzielczości instancji |
|            `0xFF` | invalid / MASK / no value         | Nie      | Kontekstowo                           |
|  scheme-dependent | Event filtrowany / progowy        | Nie      | Wymaga konfiguracji 304               |

Dla dekodera minimalnego:

```text
instance_type = 0x04
event = light_sensor_event
raw_value = event_information
```

---

# 17. IEC 62386-305 — Colour sensor events

| Event information | Znaczenie                                   | Backward | Uwagi                                |
| ----------------: | ------------------------------------------- | -------- | ------------------------------------ |
|       `0x00–0xFE` | Encoded colour-related value                | Nie      | Typ wartości zależny od konfiguracji |
|            `0xFF` | invalid / MASK                              | Nie      | Kontekstowo                          |
|  scheme-dependent | Tc / xy / RGBW / kanał zależny od instancji | Nie      | Wymaga szczegółowej tabeli 305       |

---

# 18. IEC 62386-306 — General purpose sensor events

| Event information | Znaczenie                       | Backward | Uwagi                   |
| ----------------: | ------------------------------- | -------- | ----------------------- |
|       `0x00–0xFE` | Encoded sensor value            | Nie      | Wartość ogólna          |
|            `0xFF` | invalid / MASK                  | Nie      | Kontekstowo             |
|  scheme-dependent | Wartość zależna od typu sensora | Nie      | Wymaga konfiguracji 306 |

---

# 19. IEC 62386-307 — Thermal / temperature sensor events

| Event information | Znaczenie                           | Backward | Uwagi                   |
| ----------------: | ----------------------------------- | -------- | ----------------------- |
|       `0x00–0xFE` | Encoded temperature / thermal value | Nie      | Skala zależna od 307    |
|            `0xFF` | invalid / MASK                      | Nie      | Kontekstowo             |
|  scheme-dependent | Alert / threshold / value           | Nie      | Wymaga konfiguracji 307 |

---

# 20. Dokładny algorytm klasyfikacji 24-bit frame

```text
function decode_forward24(raw):

    b0 = (raw >> 16) & 0xFF
    b1 = (raw >> 8)  & 0xFF
    b2 = raw & 0xFF

    if b0 == 0xC1:
        return decode_control_device_special(b1, b2)

    if b0 in [0xC0..0xCF]:
        return decode_special_helper_or_extended(raw)

    if b1 == 0xFE:
        address = decode_control_device_address(b0)
        opcode = b2
        return decode_device_level_command(address, opcode)

    else:
        address = decode_control_device_address(b0)
        instance = b1
        payload = b2

        if frame_direction == "from_control_device":
            return decode_input_notification(address, instance, payload)

        if frame_direction == "from_controller":
            return decode_instance_command(address, instance, payload)

        return decode_ambiguous_instance_or_event(address, instance, payload)
```

---

# 21. Heurystyka dla sniffera bez informacji o nadajniku

| Sytuacja                                                       | Klasyfikacja                          |
| -------------------------------------------------------------- | ------------------------------------- |
| `b0 == 0xC1`                                                   | Special commissioning                 |
| `b1 == 0xFE`                                                   | Device-level command/query            |
| `b1 != 0xFE`, po ramce jest backward                           | Instance query/command                |
| `b1 != 0xFE`, brak backward, ramka pojawia się asynchronicznie | Event/input notification              |
| `b2` w zakresie typowych eventów dla znanego `instance_type`   | Event                                 |
| `b2` znany jako opcode instancji                               | Instance command                      |
| brak kontekstu                                                 | Pokaż jako `instance/event ambiguous` |

---

# 22. Minimalny kontekst, który dekoder powinien pamiętać

| Pole                            | Po co                                            |
| ------------------------------- | ------------------------------------------------ |
| `device_short_address`          | Dekodowanie `byte0`                              |
| `device_groups`                 | Event scheme grupowy                             |
| `number_of_instances`           | Walidacja `byte1`                                |
| `instance_type[instance]`       | Dispatch do 3xx                                  |
| `event_scheme[instance]`        | Poprawne dekodowanie eventu                      |
| `event_filter[instance]`        | Wyjaśnienie, czemu event się pojawia/nie pojawia |
| `event_priority[instance]`      | Priorytet eventów                                |
| `memory_bank`, `memory_address` | Interpretacja `READ MEMORY LOCATION`             |
| `last_forward_expects_backward` | Interpretacja `rx_backward`                      |

---

# 23. Przykłady z Twoich logów

## 23.1 Control-device commissioning

```text
0xC105FF
0xC106FF
0xC107FF
0xC10300
rx_backward 0xFF
```

Dekoder:

```text
SEARCHADDR = 0xFFFFFF
COMPARE = YES
```

---

## 23.2 Znaleziony adres losowy

```text
0xC1053D
0xC10616
0xC10740
```

Dekoder:

```text
random/search address = 0x3D1640
```

---

## 23.3 Programowanie short address

```text
0xC10800
0xC10A00
rx_backward 0x00
0xC10400
```

Dekoder:

```text
PROGRAM SHORT ADDRESS
QUERY SHORT ADDRESS → 0x00
WITHDRAW
```

---

## 23.4 Query random address

```text
0x01FE39 → 0x2B
0x01FE3A → 0xF4
0x01FE3B → 0xF6
```

Dekoder:

```text
QUERY RANDOM ADDRESS H/M/L
random address = 0x2BF4F6
```

---

## 23.5 Read memory ASCII

```text
0x01FE3C → 0x4C
0x01FE3C → 0x75
0x01FE3C → 0x6E
0x01FE3C → 0x61
```

Dekoder:

```text
READ MEMORY LOCATION
bytes = 4C 75 6E 61
ASCII = "Luna"
```

---

# 24. Ważne ograniczenie tej wersji lookupu

Ta tabela jest gotowa jako **szkielet dekodera 24-bit DALI-2 / 103**, ale nie oznaczam jej jeszcze jako finalnej normatywnie kompletnej dla wszystkich `3xx`, bo:

```text
- eventy 3xx zależą od konkretnego typu instancji,
- różne części 301/302/303/... mają osobne tabele eventów,
- samo 103 nie wystarcza do pełnej interpretacji np. przycisku, occupancy, light sensor itd.,
- część device-level opcode 0x10–0x2F wymaga finalnej walidacji linia po linii z konkretną wersją IEC 62386-103.
```

Najbezpieczniejsze wdrożenie w snifferze na tym etapie:

```text
1. Dekoduj poprawnie klasę ramki.
2. Dekoduj pewne core opcodes: C1xxxx, C130/C131/C132, xxFE30, xxFE39/3A/3B, xxFE3C.
3. Dla pozostałych xxFEyy pokazuj:
   - opcode,
   - typ: device-level instruction/query,
   - expected backward: yes/no jeśli znane,
   - status: requires IEC 62386-103 opcode table verification.
4. Eventy xx ii ee pokazuj przez dispatch:
   - device,
   - instance,
   - event raw,
   - instance type,
   - interpretacja 3xx, jeśli znana.
```

To uchroni dekoder przed błędnym nazwaniem ramek, co jest gorsze niż pokazanie ich jako „known class / unknown opcode”.



Poniżej masz gotowe rozszerzenie do wklejenia do `DALI.md`, numerowane dalej od **25**.

````markdown
# 25. Forward24 — dodatkowa klasyfikacja ramek z czujników DALI-2

Ten rozdział rozszerza dekoder ramek 24-bitowych o obsługę ramek pochodzących z urządzeń wejściowych DALI-2, takich jak czujniki, przyciski, panele wejściowe i multisensory.

Ważne założenie:

```text
DALI-2 sensor / input device może sam nadawać 24-bit forward frame jako event/input notification.
Nie jest to backward frame.
Backward frame nadal ma 8 bitów.
````

Format ramki 24-bit:

```text
raw = 0xAABBCC

byte0 = AA
byte1 = BB
byte2 = CC
```

Ogólna interpretacja dla ramek instancyjnych:

```text
[ byte0 ][ byte1 ][ byte2 ]
[ source/address ][ instance ][ event information / opcode ]
```

---

# 26. Forward24 — priorytet klasyfikacji

Dekoder powinien klasyfikować ramki 24-bitowe w określonej kolejności. Jest to istotne, ponieważ niektóre ramki specjalne, np. `0xC9FFFF`, mogą zostać błędnie zaklasyfikowane jako event instancji, jeżeli fallback zostanie wykonany zbyt wcześnie.

| Priorytet | Warunek                                                                                 | Klasa dekodera                        | Znaczenie                                        |
| --------: | --------------------------------------------------------------------------------------- | ------------------------------------- | ------------------------------------------------ |
|         1 | `byte0 == 0xC1`                                                                         | `forward24_control_device_special`    | Special commands / commissioning control devices |
|         2 | `byte0 >= 0xC0 && byte0 <= 0xCF`                                                        | `forward24_special_or_helper`         | DTR, memory helper, special 103 command space    |
|         3 | `byte1 == 0xFE`                                                                         | `forward24_device_level_command`      | Device-level command/query: `xx FE yy`           |
|         4 | `byte0 == 0xFF && byte1 == 0xFE`                                                        | `forward24_broadcast_device_level`    | Broadcast device-level command                   |
|         5 | `byte0` jest poprawnym adresem krótkim i `byte1 != 0xFE`, a po ramce nie ma backward    | `forward24_input_notification`        | Event/input notification z instancji             |
|         6 | `byte0` jest poprawnym adresem krótkim i `byte1 != 0xFE`, a po ramce występuje backward | `forward24_instance_command_or_query` | Instance command/query                           |
|         7 | pozostałe                                                                               | `forward24_unknown_or_ambiguous`      | Nieznana lub niepełna interpretacja              |

Reguła implementacyjna:

```text
Nie klasyfikuj ramek 0xC0xxxx–0xCFxxxx jako eventów instancji.
Ten zakres powinien być obsłużony wcześniej jako special/helper.
```

---

# 27. Forward24 input notification / instance event

Klasa:

```text
forward24_input_notification
```

Format:

```text
[ source address ][ instance number ][ event information ]
```

| Pole              | Znaczenie                                       |
| ----------------- | ----------------------------------------------- |
| `byte0`           | adres źródłowego control device                 |
| `byte1`           | numer instancji                                 |
| `byte2`           | event information / event code                  |
| Backward expected | `false`                                         |
| Typ ramki         | 24-bit forward                                  |
| Kierunek logiczny | input device / sensor → magistrala              |
| Standard area     | IEC 62386-103 + odpowiednia część IEC 62386-3xx |

Przykład:

```text
raw = 0x01018D

byte0 = 0x01
byte1 = 0x01
byte2 = 0x8D
```

Dekodowanie:

```text
frame_class: forward24_input_notification
source_short_address: 0
instance: 1
event_info: 0x8D
backward_expected: false
semantic_decode: requires instance_type from IEC 62386-3xx
```

---

# 28. Dekodowanie adresu źródłowego dla input notification

Dla typowego eventu źródłowego z urządzenia o adresie krótkim:

```text
byte0 = (short_address << 1) | 1
```

Dekoder:

```text
if (byte0 & 0x01) == 1 and byte0 <= 0x7F:
    short_address = byte0 >> 1
```

Przykłady:

| `byte0` | Dekodowanie        |
| ------: | ------------------ |
|  `0x01` | short address `0`  |
|  `0x03` | short address `1`  |
|  `0x05` | short address `2`  |
|  `0x7F` | short address `63` |

Przykład z logu:

```text
0x01018C
```

Dekodowanie:

```text
byte0 = 0x01 → short address 0
byte1 = 0x01 → instance 1
byte2 = 0x8C → event information 0x8C
```

---

# 29. Event input notification — interpretacja podstawowa

Jeżeli dekoder nie zna jeszcze typu instancji, nie powinien oznaczać ramki jako `ambiguous`, tylko jako poprawnie rozpoznany event ogólny.

Zalecana prezentacja:

```text
Name: INPUT NOTIFICATION
Status: decoded_generic
Confidence: 75–85%
Backward expected: no
```

Parametry:

```json
{
  "frame_class": "forward24_input_notification",
  "source": "short:0",
  "source_short_address": 0,
  "instance": 1,
  "event_info": "0x8D",
  "backward_expected": false,
  "semantic_decode": "requires instance_type"
}
```

Niepoprawna prezentacja:

```text
INSTANCE COMMAND / EVENT
Status: ambiguous
Confidence: 45%
```

Poprawna prezentacja:

```text
INPUT NOTIFICATION
Status: decoded_generic
Confidence: 80%
```

---

# 30. Korelacja z backward frame

Ramki `forward24_input_notification` nie oczekują odpowiedzi backward.

Reguła:

```text
Jeżeli frame_class == forward24_input_notification:
    expects_backward = false
```

Oznacza to, że brak `rx_backward` po ramce typu:

```text
0x01018C
0x01018D
```

nie jest błędem.

Tabela:

| Klasa ramki                                            | Czy oczekuje backward? |
| ------------------------------------------------------ | ---------------------- |
| `forward24_device_level_command`                       | zależnie od opcode     |
| `forward24_control_device_special COMPARE`             | tak, `0xFF` albo brak  |
| `forward24_control_device_special QUERY SHORT ADDRESS` | tak, byte albo brak    |
| `forward24_input_notification`                         | nie                    |
| `forward24_instance_command_or_query`                  | zależnie od opcode     |

---

# 31. Rozróżnienie: instance command vs input notification

Ten sam układ bajtów:

```text
[ address ][ instance ][ payload ]
```

może oznaczać command/query albo event. Rozróżnienie zależy od kontekstu.

| Kryterium | Instance command/query             | Input notification/event |
| --------- | ---------------------------------- | ------------------------ |
| Nadawca   | application controller             | control device / sensor  |
| Backward  | może wystąpić                      | nie występuje            |
| Timing    | zwykle część transakcji kontrolera | często asynchroniczne    |
| `byte1`   | numer instancji                    | numer instancji          |
| `byte2`   | opcode / parametr                  | event information        |
| Klasa UI  | `INSTANCE COMMAND/QUERY`           | `INPUT NOTIFICATION`     |

Heurystyka dla sniffera bez informacji o fizycznym nadajniku:

```text
if byte1 != 0xFE
and byte0 is valid short-addressed source
and no backward follows in the response window
and frame is not in special/helper range:
    classify as forward24_input_notification
```

---

# 32. Kontekst instancji wymagany do pełnego dekodowania eventu

Samo `event_info = 0x8D` nie wystarcza do pełnego semantycznego opisu zdarzenia.

Dekoder powinien utrzymywać kontekst dla każdego control device:

| Pole kontekstu        | Źródło informacji             | Po co                               |
| --------------------- | ----------------------------- | ----------------------------------- |
| `short_address`       | commissioning / scan          | identyfikacja urządzenia            |
| `number_of_instances` | query device-level            | walidacja numeru instancji          |
| `instance_type[n]`    | query instancji / memory bank | dispatch do właściwej części 3xx    |
| `event_scheme[n]`     | konfiguracja instancji        | interpretacja formatu eventu        |
| `event_filter[n]`     | konfiguracja instancji        | informacja, które eventy są aktywne |
| `event_priority[n]`   | konfiguracja                  | priorytet eventu                    |
| `instance_group[n]`   | konfiguracja                  | event routing / grupy instancji     |

Jeżeli `instance_type` jest nieznany:

```text
Nie zgaduj znaczenia eventu.
Pokaż event jako generic input notification.
```

---

# 33. Dispatch eventów według instance type

Po odczytaniu typu instancji dekoder powinien przekazać `event_info` do odpowiedniego dekodera części 3xx.

| Instance type | IEC part      | Typ instancji                | Dekoder eventu                                |
| ------------: | ------------- | ---------------------------- | --------------------------------------------- |
|        `0x01` | IEC 62386-301 | Push button                  | `decode_301_push_button_event(event_info)`    |
|        `0x02` | IEC 62386-302 | Absolute input               | `decode_302_absolute_input_event(event_info)` |
|        `0x03` | IEC 62386-303 | Occupancy sensor             | `decode_303_occupancy_event(event_info)`      |
|        `0x04` | IEC 62386-304 | Light sensor                 | `decode_304_light_event(event_info)`          |
|        `0x05` | IEC 62386-305 | Colour sensor                | `decode_305_colour_event(event_info)`         |
|        `0x06` | IEC 62386-306 | General purpose sensor       | `decode_306_gp_sensor_event(event_info)`      |
|        `0x07` | IEC 62386-307 | Thermal / temperature sensor | `decode_307_thermal_event(event_info)`        |
|       unknown | —             | Unknown instance type        | pokaż raw event information                   |

Fallback:

```text
INPUT NOTIFICATION
instance_type: unknown
event_info: 0x8D
semantic_name: unavailable
```

---

# 34. Event scheme — wpływ na interpretację eventu

DALI-2 control devices mogą używać różnych schematów zdarzeń. Dlatego dekoder powinien oddzielać:

```text
rozpoznanie ramki jako eventu
```

od:

```text
semantycznego nazwania eventu
```

Tabela:

| Poziom dekodowania    | Wymagany kontekst                                     | Przykład wyniku                                            |
| --------------------- | ----------------------------------------------------- | ---------------------------------------------------------- |
| Generic frame decode  | tylko raw 24-bit                                      | `INPUT NOTIFICATION, short:0, instance:1, event_info:0x8D` |
| Instance-aware decode | znany `instance_type`                                 | `Push button event 0x8D` albo `Occupancy event 0x8D`       |
| Full semantic decode  | znany `instance_type`, `event_scheme`, `event_filter` | konkretna nazwa zdarzenia zgodna z 3xx                     |

Jeżeli event scheme nie jest znany:

```text
status: decoded_generic
warning: event scheme unknown
```

---

# 35. Przykłady dekodowania eventów z sensorów

## 35.1 Event `0x01018C`

Raw:

```text
0x01018C
```

Dekodowanie:

```text
byte0 = 0x01
byte1 = 0x01
byte2 = 0x8C
```

Wynik:

```text
frame_class: forward24_input_notification
name: INPUT NOTIFICATION
source_short_address: 0
instance: 1
event_info: 0x8C
backward_expected: false
status: decoded_generic
```

## 35.2 Event `0x01018D`

Raw:

```text
0x01018D
```

Dekodowanie:

```text
byte0 = 0x01
byte1 = 0x01
byte2 = 0x8D
```

Wynik:

```text
frame_class: forward24_input_notification
name: INPUT NOTIFICATION
source_short_address: 0
instance: 1
event_info: 0x8D
backward_expected: false
status: decoded_generic
```

---

# 36. Special/helper range — zapobieganie błędnej klasyfikacji

Ramki z zakresu:

```text
0xC0xxxx–0xCFxxxx
```

nie powinny być automatycznie klasyfikowane jako eventy instancji.

Przykład problematyczny:

```text
0xC9FFFF
```

Niepoprawnie:

```text
INSTANCE COMMAND / EVENT
status: ambiguous
```

Poprawnie:

```text
forward24_special_or_helper
status: decoded_class_only
```

Reguła:

```text
if byte0 >= 0xC0 and byte0 <= 0xCF:
    classify as forward24_special_or_helper
    stop generic instance/event fallback
```

Wyjątek szczegółowy:

```text
byte0 == 0xC1
```

powinien być wcześniej dekodowany jako:

```text
forward24_control_device_special
```

czyli commissioning control devices.

---

# 37. Device-level command vs input notification

Ramki device-level mają zawsze:

```text
byte1 == 0xFE
```

Przykład:

```text
0x01FE30
```

Dekodowanie:

```text
byte0 = 0x01 → short address 0
byte1 = 0xFE → device-level command/query
byte2 = 0x30 → opcode
```

Klasa:

```text
forward24_device_level_command
```

Natomiast ramki:

```text
0x01018C
0x01018D
```

mają:

```text
byte1 = 0x01
```

czyli nie są device-level command. Są to ramki instancyjne:

```text
source short address 0
instance 1
payload/event_info 0x8C / 0x8D
```

Jeżeli brak backward i ramka nie jest częścią transakcji kontrolera, klasyfikuj jako:

```text
forward24_input_notification
```

---

# 38. Proponowany pseudocode dla forward24

```text
function decode_forward24(raw, context):

    b0 = (raw >> 16) & 0xFF
    b1 = (raw >> 8)  & 0xFF
    b2 = raw & 0xFF

    # 1. Control device commissioning / special commands
    if b0 == 0xC1:
        return decode_forward24_control_device_special(b1, b2)

    # 2. Other special/helper space
    if b0 >= 0xC0 and b0 <= 0xCF:
        return {
            frame_class: "forward24_special_or_helper",
            name: decode_special_helper_name_or_unknown(b0, b1, b2),
            params: {
                "byte0": hex(b0),
                "byte1": hex(b1),
                "byte2": hex(b2)
            },
            status: "decoded_class_only"
        }

    # 3. Device-level command/query
    if b1 == 0xFE:
        address = decode_control_device_address(b0)
        return decode_forward24_device_level(address, b2)

    # 4. Instance/event format
    if is_valid_short_address_byte(b0):
        source_short = b0 >> 1
        instance = b1
        payload = b2

        if context.backward_follows_current_frame:
            return {
                frame_class: "forward24_instance_command_or_query",
                name: "INSTANCE COMMAND / QUERY",
                addressing: "short:" + source_short,
                params: {
                    "instance": instance,
                    "opcode": hex(payload)
                },
                status: "decoded_generic"
            }

        else:
            return {
                frame_class: "forward24_input_notification",
                name: "INPUT NOTIFICATION",
                addressing: "short:" + source_short,
                params: {
                    "instance": instance,
                    "event_info": hex(payload)
                },
                backward_expected: false,
                status: "decoded_generic"
            }

    # 5. Unknown fallback
    return {
        frame_class: "forward24_unknown_or_ambiguous",
        name: "UNKNOWN FORWARD24",
        params: {
            "byte0": hex(b0),
            "byte1": hex(b1),
            "byte2": hex(b2)
        },
        status: "ambiguous"
    }
```

---

# 39. Funkcja pomocnicza: valid short address byte

```text
function is_valid_short_address_byte(byte0):
    return ((byte0 & 0x01) == 1) and (byte0 <= 0x7F)
```

Przykłady:

| `byte0` | Wynik                                       | Znaczenie                   |
| ------: | ------------------------------------------- | --------------------------- |
|  `0x01` | valid                                       | short address 0             |
|  `0x03` | valid                                       | short address 1             |
|  `0x7F` | valid                                       | short address 63            |
|  `0x00` | invalid for command-source short addressing | selector bit = 0            |
|  `0x80` | invalid for short source                    | poza zakresem short address |
|  `0xC1` | invalid here                                | special command range       |
|  `0xFF` | invalid here                                | broadcast/special           |

---

# 40. Zalecany output UI dla input notification

Dla ramki:

```text
0x01018D
```

UI powinien pokazać:

| Pole              | Wartość                                                         |
| ----------------- | --------------------------------------------------------------- |
| Raw               | `0x01018D`                                                      |
| Direction         | `rx_forward24`                                                  |
| Name              | `INPUT NOTIFICATION`                                            |
| Status            | `decoded_generic`                                               |
| Frame class       | `forward24_input_notification`                                  |
| Addressing        | `short:0`                                                       |
| Instance          | `1`                                                             |
| Event information | `0x8D`                                                          |
| Backward expected | `false`                                                         |
| Confidence        | `80%`                                                           |
| Note              | `Semantic event name requires instance type from IEC 62386-3xx` |

JSON/details:

```json
{
  "frame_class": "forward24_input_notification",
  "name": "INPUT NOTIFICATION",
  "addressing": "short:0",
  "source_short_address": 0,
  "instance": 1,
  "event_info": "0x8D",
  "backward_expected": false,
  "semantic_decode": "requires instance_type",
  "status": "decoded_generic"
}
```

---

# 41. Reguła confidence dla forward24 input notification

| Warunek                                                                                |                  Confidence |
| -------------------------------------------------------------------------------------- | --------------------------: |
| Poprawny `byte0` jako short address, `byte1 != 0xFE`, brak backward, nie special range |                       `80%` |
| Dodatkowo znany `instance_type` dla tej instancji                                      |                       `90%` |
| Dodatkowo znany `event_scheme`                                                         |                       `95%` |
| Nieznany `instance_type`, ale ramka pojawia się asynchronicznie                        |                       `80%` |
| Nieznany kierunek nadajnika i w pobliżu są komendy kontrolera                          |                    `60–70%` |
| `byte0` w zakresie `0xC0–0xCF`                                                         | nie klasyfikować jako event |

---

# 42. Test vectors dla dekodera

| Raw        | Oczekiwana klasa                   | Name                                 | Params                                     | Backward expected                |
| ---------- | ---------------------------------- | ------------------------------------ | ------------------------------------------ | -------------------------------- |
| `0x01018C` | `forward24_input_notification`     | `INPUT NOTIFICATION`                 | `short:0`, `instance:1`, `event_info:0x8C` | `false`                          |
| `0x01018D` | `forward24_input_notification`     | `INPUT NOTIFICATION`                 | `short:0`, `instance:1`, `event_info:0x8D` | `false`                          |
| `0x01FE30` | `forward24_device_level_command`   | device-level opcode `0x30`           | `short:0`, `opcode:0x30`                   | depends on opcode                |
| `0x01FE3C` | `forward24_device_level_command`   | `READ MEMORY LOCATION`               | `short:0`, `opcode:0x3C`                   | `true`, byte                     |
| `0xC10300` | `forward24_control_device_special` | `COMPARE`                            | none                                       | `true`, yes/no                   |
| `0xC105FF` | `forward24_control_device_special` | `SEARCHADDRH`                        | `0xFF`                                     | `false`                          |
| `0xC9FFFF` | `forward24_special_or_helper`      | special/helper unknown               | `byte0:0xC9`                               | context-dependent                |
| `0xFFFE1D` | `forward24_broadcast_device_level` | broadcast device-level opcode `0x1D` | `broadcast`, `opcode:0x1D`                 | usually false / opcode-dependent |

---

# 43. Known limitation — semantic event decoding

Na tym etapie dekoder może poprawnie rozpoznać:

```text
INPUT NOTIFICATION
source short address
instance
event information
```

ale nie zawsze może poprawnie nazwać zdarzenie jako np.:

```text
button pressed
presence detected
light level changed
temperature event
```

Do tego wymagane jest:

```text
instance_type
event_scheme
część IEC 62386-3xx właściwa dla danej instancji
```

Dlatego zalecany fallback:

```text
INPUT NOTIFICATION / semantic event unknown
```

zamiast:

```text
ambiguous
```

---

# 44. Minimalna zmiana wymagana w dekoderze

Aby ramki sensorów przestały wpadać jako `ambiguous`, wystarczy dodać:

```text
1. Priorytetowe wykluczenie zakresu 0xC0xxxx–0xCFxxxx.
2. Osobną klasę `forward24_input_notification`.
3. Regułę:
   if byte0 is valid short address
   and byte1 != 0xFE
   and no backward follows
   then INPUT NOTIFICATION.
4. Fallback semantyczny:
   jeśli instance_type unknown → decoded_generic, nie ambiguous.
```

Przykładowy wynik dla Twojego przypadku:

```text
raw: 0x01018D
old:
    INSTANCE COMMAND / EVENT
    status: ambiguous
    confidence: 45%

new:
    INPUT NOTIFICATION
    status: decoded_generic
    confidence: 80%
    source: short:0
    instance: 1
    event_info: 0x8D
    backward_expected: false
```

```
```
