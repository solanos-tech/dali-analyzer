# DALI Decoder Lookup - IEC 62386-101/102/103

```text
IEC 62386-101 - system layer / frame types / timing / forward/backward
IEC 62386-102 - control gear: power supplies, ballasts, LED drivers
IEC 62386-103 - control devices: sensors, push buttons, panels, input controllers
```

---

## 1. Frame Types - IEC 62386-101

| Frame type         | Logical direction                    | Data bits | Log example                 | Meaning for decoder                                     |
| ------------------ | ------------------------------------ | --------- | --------------------------- | ------------------------------------------------------- |
| Forward 16-bit     | master/control device -> control gear| 16        | `rx_forward16 raw=0xA900`   | Classic DALI commands to control gear, part 102         |
| Forward 24-bit     | control device / controller -> bus   | 24        | `rx_forward24 raw=0x01FE3C` | DALI-2 control-device commands and events, part 103     |
| Forward 32-bit     | controller -> bus                    | 32        | not present in logs         | Firmware/update/data transfer; outside current scope    |
| Backward 8-bit     | device response                      | 8         | `rx_backward raw=0xFF`      | Response to query/compare/verify                        |
| Corrupted backward | colliding / damaged response         | invalid   | depends on sniffer          | May occur when multiple devices respond differently     |

Backward frames **always use 8 data bits**, including DALI-2. The difference between DALI-1 and DALI-2 mainly affects forward frames, not backward frames.

---

## 2. Forward 16-bit - General Structure

Frame:

```text
[ byte 0 ][ byte 1 ]
```

Bitwise:

```text
byte0: AAAAAA S / addressing type
byte1: command or arc power level
```

### 2.1 Addressing in forward16

| Condition / mask         | `byte0` range                       | Type              | Bit decoding  | Meaning                           |
| ------------------------ | ----------------------------------- | ----------------- | ------------- | --------------------------------- |
| `(byte0 & 0x80) == 0x00` | `0x00-0x7F`                         | Short address     | `AAAAAA S`    | Individual control-gear address   |
| `(byte0 & 0xE0) == 0x80` | `0x80-0x9F`                         | Group address     | `100 GGGG S`  | Group address 0-15                |
| `byte0 == 0xFE`          | `0xFE`                              | Broadcast DAPC    | -             | Broadcast direct arc power        |
| `byte0 == 0xFF`          | `0xFF`                              | Broadcast command | -             | Broadcast command/query           |
| `byte0 in special range` | e.g. `0xA1`, `0xA3`, `0xA5`, `0xA7` | Special command   | command-specific | Commissioning, DTR, search address |

#### Bit `S`

| `S` | Meaning                                             |
| --: | --------------------------------------------------- |
| `0` | Direct Arc Power Control, second byte = light level |
| `1` | Command / query, second byte = opcode               |

Examples:

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

## 3. Forward 16-bit - Direct Arc Power Control

| Condition           | Format                  | Meaning                                     | Backward | Send twice |
| ------------------- | ----------------------- | ------------------------------------------- | -------- | ---------- |
| `S=0`               | `[address byte][level]` | Set arc/light level                         | No       | No         |
| `level = 0x00`      | OFF / minimum by state  | Level 0                                     | No       | No         |
| `level = 0x01-0xFE` | level 1-254             | Brightness level                            | No       | No         |
| `level = 0xFF`      | MASK                    | No change / mask value depending on context | No       | No         |

Example:

```text
0x0080
short address 0
DAPC level = 0x80
```

---

## 4. Forward 16-bit - Control-Gear Commands, IEC 62386-102

### 4.1 Level-control commands

| Opcode      | Name                    | Meaning                                  | Backward | Send twice | Notes            |
| ----------- | ----------------------- | ---------------------------------------- | -------- | ---------- | ---------------- |
| `0x00`      | OFF                     | Turn light off                           | No       | No         | Addressed command |
| `0x01`      | UP                      | Brighten according to fade rate          | No       | No         | Iterative        |
| `0x02`      | DOWN                    | Dim according to fade rate               | No       | No         | Iterative        |
| `0x03`      | STEP UP                 | Step up                                  | No       | No         |                  |
| `0x04`      | STEP DOWN               | Step down                                | No       | No         |                  |
| `0x05`      | RECALL MAX LEVEL        | Go to max level                          | No       | No         |                  |
| `0x06`      | RECALL MIN LEVEL        | Go to min level                          | No       | No         |                  |
| `0x07`      | STEP DOWN AND OFF       | Step down; switch off if already minimum | No       | No         |                  |
| `0x08`      | ON AND STEP UP          | Switch on and step up                    | No       | No         |                  |
| `0x09`      | ENABLE DAPC SEQUENCE    | Enable DAPC sequence                     | No       | No         | DALI-2           |
| `0x0A`      | GO TO LAST ACTIVE LEVEL | Return to last active level              | No       | No         | DALI-2           |
| `0x0B-0x0F` | Reserved                | Do not decode as known command           | -        | -          | Mark as reserved |

### 4.2 Scenes

| Opcode / mask | Name            | Parameter           | Backward | Send twice |
| ------------- | --------------- | ------------------- | -------- | ---------- |
| `0x10-0x1F`   | GO TO SCENE `n` | `n = opcode & 0x0F` | No       | No         |

Example:

```text
0x0114
short address 0
GO TO SCENE 4
```

### 4.3 Configuration commands

| Opcode      | Name                       | Parameter                      | Backward | Send twice                    | Notes                     |
| ----------- | -------------------------- | ------------------------------ | -------- | ----------------------------- | ------------------------- |
| `0x20`      | RESET                      | Reset control-gear parameters  | No       | Yes                           | Changes configuration     |
| `0x21`      | STORE ACTUAL LEVEL IN DTR0 | Store current level into DTR0  | No       | Yes                           |                           |
| `0x22`      | SAVE PERSISTENT VARIABLES  | Force persistent save          | No       | Yes                           | DALI-2                    |
| `0x23`      | SET OPERATING MODE         | Value from DTR0                | No       | Yes                           |                           |
| `0x24`      | RESET MEMORY BANK          | Bank from DTR0                 | No       | Yes                           |                           |
| `0x25`      | IDENTIFY DEVICE            | Device identification mode     | No       | No / implementation-dependent | DALI-2                    |
| `0x26`      | RESET POWER CYCLE SEEN     | Clear power-cycle-seen flag    | No       | Yes                           | DALI-2                    |
| `0x27-0x29` | Reserved                   | -                              | -        | -                             |                           |

### 4.4 Store DTR0 as...

| Opcode | Name                               | Parameter | Backward | Send twice |
| ------ | ---------------------------------- | --------- | -------- | ---------- |
| `0x2A` | STORE DTR0 AS MAX LEVEL            | `DTR0`    | No       | Yes        |
| `0x2B` | STORE DTR0 AS MIN LEVEL            | `DTR0`    | No       | Yes        |
| `0x2C` | STORE DTR0 AS SYSTEM FAILURE LEVEL | `DTR0`    | No       | Yes        |
| `0x2D` | STORE DTR0 AS POWER ON LEVEL       | `DTR0`    | No       | Yes        |
| `0x2E` | STORE DTR0 AS FADE TIME            | `DTR0`    | No       | Yes        |
| `0x2F` | STORE DTR0 AS FADE RATE            | `DTR0`    | No       | Yes        |

### 4.5 Store / remove / add scene and group

| Opcode / mask | Name                    | Parameter           | Backward | Send twice |
| ------------- | ----------------------- | ------------------- | -------- | ---------- |
| `0x30-0x3F`   | STORE DTR0 AS SCENE `n` | `n = opcode & 0x0F` | No       | Yes        |
| `0x40-0x4F`   | REMOVE FROM SCENE `n`   | `n = opcode & 0x0F` | No       | Yes        |
| `0x50-0x5F`   | ADD TO GROUP `n`        | `n = opcode & 0x0F` | No       | Yes        |
| `0x60-0x6F`   | REMOVE FROM GROUP `n`   | `n = opcode & 0x0F` | No       | Yes        |

### 4.6 Short address / memory write

| Opcode      | Name                | Parameter | Backward | Send twice | Notes                                |
| ----------- | ------------------- | --------- | -------- | ---------- | ------------------------------------ |
| `0x70`      | SET SHORT ADDRESS   | `DTR0`    | No       | Yes        | `DTR0 = (short << 1) | 1` or `MASK` |
| `0x71`      | ENABLE WRITE MEMORY | -         | No       | Yes        | Allows memory-bank write             |
| `0x72-0x7F` | Reserved            | -         | -        | -          |                                      |

---

## 5. Forward 16-bit - Query Control Gear

### 5.1 Query status and flags

| Opcode | Name                         | Backward       | Response interpretation        |
| ------ | ---------------------------- | -------------- | ------------------------------ |
| `0x90` | QUERY STATUS                 | Status byte    | Bit response, see table below  |
| `0x91` | QUERY CONTROL GEAR PRESENT   | `0xFF` or none | `0xFF = YES`, no response = NO |
| `0x92` | QUERY LAMP FAILURE           | `0xFF` or none | `YES/NO`                       |
| `0x93` | QUERY LAMP POWER ON          | `0xFF` or none | `YES/NO`                       |
| `0x94` | QUERY LIMIT ERROR            | `0xFF` or none | `YES/NO`                       |
| `0x95` | QUERY RESET STATE            | `0xFF` or none | `YES/NO`                       |
| `0x96` | QUERY MISSING SHORT ADDRESS  | `0xFF` or none | `YES/NO`                       |
| `0x97` | QUERY VERSION NUMBER         | Byte           | Version number                 |
| `0x98` | QUERY CONTENT DTR0           | Byte           | Current DTR0                   |
| `0x99` | QUERY DEVICE TYPE            | Byte           | Device type                    |
| `0x9A` | QUERY PHYSICAL MINIMUM LEVEL | Byte           | Physical minimum level         |
| `0x9B` | QUERY POWER FAILURE          | `0xFF` or none | `YES/NO`                       |
| `0x9C` | QUERY CONTENT DTR1           | Byte           | Current DTR1                   |
| `0x9D` | QUERY CONTENT DTR2           | Byte           | Current DTR2                   |
| `0x9E` | QUERY OPERATING MODE         | Byte           | Operating mode                 |
| `0x9F` | QUERY LIGHT SOURCE TYPE      | Byte           | Light-source type              |

#### QUERY STATUS response bits

| Bit | Mask   | Meaning                    |
| --- | ------ | -------------------------- |
| 0   | `0x01` | Control gear failure       |
| 1   | `0x02` | Lamp failure               |
| 2   | `0x04` | Lamp power on              |
| 3   | `0x08` | Limit error                |
| 4   | `0x10` | Fade running / fade active |
| 5   | `0x20` | Reset state                |
| 6   | `0x40` | Missing short address      |
| 7   | `0x80` | Power failure seen         |

### 5.2 Query level / configuration values

| Opcode      | Name                             | Backward                  | Interpretation             |
| ----------- | -------------------------------- | ------------------------- | -------------------------- |
| `0xA0`      | QUERY ACTUAL LEVEL               | Byte                      | Current level              |
| `0xA1`      | QUERY MAX LEVEL                  | Byte                      | Max level                  |
| `0xA2`      | QUERY MIN LEVEL                  | Byte                      | Min level                  |
| `0xA3`      | QUERY POWER ON LEVEL             | Byte                      | Power-on level             |
| `0xA4`      | QUERY SYSTEM FAILURE LEVEL       | Byte                      | System-failure level       |
| `0xA5`      | QUERY FADE TIME / FADE RATE      | Byte                      | High/low nibble            |
| `0xA6`      | QUERY MANUFACTURER SPECIFIC MODE | Byte or YES/NO by version | Context-dependent          |
| `0xA7`      | QUERY NEXT DEVICE TYPE           | Byte                      | Next supported device type |
| `0xA8`      | QUERY EXTENDED FADE TIME         | Byte                      | Encoded extended fade time |
| `0xA9`      | QUERY CONTROL GEAR FAILURE       | `0xFF` or none            | `YES/NO`                   |
| `0xAA-0xAF` | Reserved                         | -                         | -                          |

#### `QUERY FADE TIME / FADE RATE`

| Bits     | Meaning   |
| -------- | --------- |
| `b7..b4` | fade time |
| `b3..b0` | fade rate |

### 5.3 Query scenes

| Opcode / mask | Name                  | Parameter           | Backward             |
| ------------- | --------------------- | ------------------- | -------------------- |
| `0xB0-0xBF`   | QUERY SCENE LEVEL `n` | `n = opcode & 0x0F` | Byte level or `MASK` |

### 5.4 Query groups / random address / memory

| Opcode      | Name                          | Backward       | Interpretation                    |
| ----------- | ----------------------------- | -------------- | --------------------------------- |
| `0xC0`      | QUERY GROUPS 0-7              | Bitmap byte    | Bits 0-7 = groups 0-7             |
| `0xC1`      | QUERY GROUPS 8-15             | Bitmap byte    | Bits 0-7 = groups 8-15            |
| `0xC2`      | QUERY RANDOM ADDRESS H        | Byte           | High byte of random address       |
| `0xC3`      | QUERY RANDOM ADDRESS M        | Byte           | Middle byte of random address     |
| `0xC4`      | QUERY RANDOM ADDRESS L        | Byte           | Low byte of random address        |
| `0xC5`      | READ MEMORY LOCATION          | Byte           | Read bank/address selected by DTR |
| `0xC6-0xDF` | Reserved                      | -              | -                                 |
| `0xE0-0xFF` | Application extended commands | device-specific| Parts 2xx, outside current scope  |

Example from your log:

```text
0x01C2 -> rx_backward 0x4E
0x01C3 -> rx_backward 0x4C
0x01C4 -> rx_backward 0xD3
```

Interpretation:

```text
short address 0
QUERY RANDOM ADDRESS H/M/L
random address = 0x4E4CD3
```

---

## 6. Forward 16-bit - Special Commands / Commissioning

These commands do not use the standard control-gear address field. They are decoded by the first byte.

| Raw pattern | Name                  | Parameter | Backward           | Send twice | Meaning                                     |
| ----------- | --------------------- | --------- | ------------------ | ---------- | ------------------------------------------- |
| `0xA100`    | TERMINATE             | -         | No                 | No         | End initialization mode                     |
| `0xA3xx`    | SET DTR0              | `xx`      | No                 | No         | Set DTR0                                    |
| `0xA5xx`    | INITIALISE            | `xx`      | No                 | Yes        | Enter initialization mode                   |
| `0xA700`    | RANDOMISE             | -         | No                 | Yes        | Generate 24-bit random address              |
| `0xA900`    | COMPARE               | -         | `0xFF` or none     | No         | `YES` if `random_address <= search_address` |
| `0xAB00`    | WITHDRAW              | -         | No                 | No         | Remove found device from further search     |
| `0xB1xx`    | SEARCHADDRH           | `xx`      | No                 | No         | Set high byte of search address             |
| `0xB3xx`    | SEARCHADDRM           | `xx`      | No                 | No         | Set middle byte of search address           |
| `0xB5xx`    | SEARCHADDRL           | `xx`      | No                 | No         | Set low byte of search address              |
| `0xB7xx`    | PROGRAM SHORT ADDRESS | `xx`      | No                 | No         | Program short address of selected device    |
| `0xB9xx`    | VERIFY SHORT ADDRESS  | `xx`      | `0xFF` or none     | No         | Verify short address                        |
| `0xBB00`    | QUERY SHORT ADDRESS   | -         | Byte or none       | No         | Read encoded short address                  |
| `0xBD00`    | PHYSICAL SELECTION    | -         | No                 | No         | Physical device selection, if supported     |
| `0xC1xx`    | ENABLE DEVICE TYPE    | `xx`      | No                 | No         | Enable extended device-type commands        |
| `0xC3xx`    | SET DTR1              | `xx`      | No                 | No         | Set DTR1                                    |
| `0xC5xx`    | SET DTR2              | `xx`      | No                 | No         | Set DTR2                                    |
| `0xC7xx`    | WRITE MEMORY LOCATION | `xx`      | Byte or none       | Contextual | Write to memory bank                        |

Example from your log:

```text
0xB1FF
0xB3FF
0xB5FF
0xA900 -> 0xFF
```

Interpretation:

```text
SEARCHADDR = 0xFFFFFF
COMPARE = YES
```

---

## 7. Short-Address Encoding

### 7.1 In addressed forward16

```text
byte0 = (short_address << 1) | S
```

| Field            | Meaning         |
| ---------------- | --------------- |
| `short_address`  | `0-63`          |
| `S=0`            | DAPC            |
| `S=1`            | Command/query   |

Example:

```text
short address 0, command:
(0 << 1) | 1 = 0x01
```

```text
0x0191 = short address 0, QUERY CONTROL GEAR PRESENT
```

### 7.2 In `PROGRAM SHORT ADDRESS`

```text
data = (short_address << 1) | 1
```

Example:

```text
short address 0 -> data = 0x01
0xB701 = PROGRAM SHORT ADDRESS 0
```

---

## 8. Backward Interpretation Rules

Backward frames must always be interpreted against the previous forward frame.

| Previous command       | Backward `0xFF` | No backward | Other byte          |
| ---------------------- | --------------- | ----------- | ------------------- |
| `COMPARE`              | YES             | NO          | unusual / corrupted |
| `QUERY ... YES/NO`     | YES             | NO          | unusual             |
| `QUERY STATUS`         | status byte     | no response | status byte         |
| `QUERY LEVEL`          | value 0-254/255 | no response | value               |
| `READ MEMORY LOCATION` | data byte       | no response | data byte           |
| `QUERY SHORT ADDRESS`  | encoded address | no response | address byte        |
| `VERIFY SHORT ADDRESS` | YES             | NO          | unusual             |

Important decoder note: `0xFF` does not always mean only `YES`. For some queries it may also represent value `255` or `MASK`.

---

## 9. Forward 24-bit - IEC 62386-103, Control Devices

Frame:

```text
[ byte0 ][ byte1 ][ byte2 ]
```

Examples from your log:

```text
0xC10300
0x01FE3C
0x01018D
```

### 9.1 forward24 frame classes

| Condition / pattern         | Class                                           | Meaning                                              |
| --------------------------- | ----------------------------------------------- | ---------------------------------------------------- |
| `byte0 == 0xC1`             | Special command / commissioning control devices | DALI-2 control-device discovery and addressing       |
| `byte1 == 0xFE`             | Device-level command/query                      | Commands to the whole control device                 |
| `byte1 != 0xFE`             | Instance/event related                          | Events or instance commands                          |
| `byte0 == 0xFF`             | Broadcast control-device command                | Broadcast to control devices                         |
| `byte0 == (short << 1) | 1` | Short-addressed control-device command          | Command to control device at given short address     |

---

## 10. Forward 24-bit - Commissioning Control Devices

Based on IEC 62386-103, the mechanism is analogous to control gear, but uses 24-bit frames.

| Raw pattern | Name                  | Parameter | Backward       | Send twice | Meaning                                     |
| ----------- | --------------------- | --------- | -------------- | ---------- | ------------------------------------------- |
| `0xC10000`  | TERMINATE             | -         | No             | No         | End control-device initialization mode      |
| `0xC101xx`  | INITIALISE            | `xx`      | No             | Yes        | Enter control-device initialization mode    |
| `0xC10200`  | RANDOMISE             | -         | No             | Yes        | Generate random address                     |
| `0xC10300`  | COMPARE               | -         | `0xFF` or none | No         | `YES` if `random_address <= search_address` |
| `0xC10400`  | WITHDRAW              | -         | No             | No         | Remove found device from search             |
| `0xC105xx`  | SEARCHADDRH           | `xx`      | No             | No         | High byte of search address                 |
| `0xC106xx`  | SEARCHADDRM           | `xx`      | No             | No         | Middle byte of search address               |
| `0xC107xx`  | SEARCHADDRL           | `xx`      | No             | No         | Low byte of search address                  |
| `0xC108xx`  | PROGRAM SHORT ADDRESS | `xx`      | No             | No         | Program control-device short address        |
| `0xC109xx`  | VERIFY SHORT ADDRESS  | `xx`      | `0xFF` or none | No         | Verify short address                        |
| `0xC10A00`  | QUERY SHORT ADDRESS   | -         | Byte or none   | No         | Read short address                          |

Example from your log:

```text
0xC105FF
0xC106FF
0xC107FF
0xC10300 -> 0xFF
```

Interpretation:

```text
SEARCHADDR = 0xFFFFFF
COMPARE = YES
```

---

## 11. Forward 24-bit - DTR / Memory Helpers for Control Devices

| Raw pattern | Working name                  | Parameter | Backward          | Notes                                           |
| ----------- | ----------------------------- | --------- | ----------------- | ----------------------------------------------- |
| `0xC130xx`  | SET DTR0 / data register 0    | `xx`      | No                | Used before memory read/write                   |
| `0xC131xx`  | SET DTR1 / data register 1    | `xx`      | No                | Used as bank/index depending on command         |
| `0xC132xx`  | SET DTR2 / data register 2    | `xx`      | No                | Needs implementation confirmation               |
| `0xC9xxxx`  | WRITE / memory-related command| `xxxx`    | command-dependent | Must be validated against table 103             |

In your logs:

```text
0xC13100
0xC1308F
0x01FE3C
```

This looks like memory-pointer setup followed by sequential byte reads through `0x01FE3C`.

---

## 12. Forward 24-bit - Device-Level Commands / Queries

Pattern:

```text
[ address byte ][ 0xFE ][ opcode ]
```

Example:

```text
0x01FE30
```

Decoding:

```text
byte0 = 0x01 -> short address 0, command
byte1 = 0xFE -> device-level command/query
byte2 = 0x30 -> opcode
```

### 12.1 Device-level query lookup - core

| Pattern    | Name                                                | Backward | Meaning                                                       |
| ---------- | --------------------------------------------------- | -------- | ------------------------------------------------------------- |
| `xx FE 30` | QUERY CONTROL DEVICE STATUS / PRESENT / core status | Byte     | Status or presence identification, depending on opcode in 103 |
| `xx FE 39` | QUERY IDENTIFICATION / RANDOM / memory-related H    | Byte     | Returns one data byte in your logs                            |
| `xx FE 3A` | QUERY IDENTIFICATION / RANDOM / memory-related M    | Byte     | Returns one data byte in your logs                            |
| `xx FE 3B` | QUERY IDENTIFICATION / RANDOM / memory-related L    | Byte     | Returns one data byte in your logs                            |
| `xx FE 3C` | READ MEMORY LOCATION                                | Byte     | Read next byte from memory bank                               |

Example from your log:

```text
0x01FE3C -> 0x4C
0x01FE3C -> 0x75
0x01FE3C -> 0x6E
0x01FE3C -> 0x61
```

ASCII:

```text
4C 75 6E 61 = "Luna"
```

---

## 13. Forward 24-bit - Event / Input Notification

General pattern:

```text
[ source/address ][ instance ][ event ]
```

Examples:

```text
0x01018C
0x01018D
```

Working decoding:

```text
byte0 = 0x01 -> short address 0 / source device
byte1 = 0x01 -> instance 1
byte2 = 0x8C / 0x8D -> event code
```

| Field             | Meaning                                  |
| ----------------- | ---------------------------------------- |
| `byte0`           | control-device address / event source    |
| `byte1`           | instance number                          |
| `byte2`           | event code                               |
| `byte2 0x80-0xBF` | typical range for events/input notifications |
| Backward          | No backward expected                     |

For the decoder:

```text
if frame24 does not have byte1 == 0xFE and is not special C1xxxx,
treat it as event/instance-related frame
```

---

## 14. Send-Twice Rules for Decoder

| Command class                 | Send twice |
| ---------------------------- | ---------- |
| DAPC                         | No         |
| Level-control commands       | Usually no |
| Query                        | No         |
| `RESET`, store/configuration | Yes        |
| `INITIALISE`                 | Yes        |
| `RANDOMISE`                  | Yes        |
| `SEARCHADDRH/M/L`            | No         |
| `COMPARE`                    | No         |
| `PROGRAM SHORT ADDRESS`      | No         |
| `VERIFY SHORT ADDRESS`       | No         |
| `WITHDRAW`                   | No         |
| `ENABLE WRITE MEMORY`        | Yes        |
| `SAVE PERSISTENT VARIABLES`  | Yes        |

For a sniffer/decoder it is useful to keep a dedicated flag:

```text
send_twice_expected = true/false
```

and warning:

```text
expected repeated frame not observed within timing window
```

---

## 15. Example Classification Rules for Decoder

### 15.1 Forward16

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

### 15.2 Forward24

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

## 16. Minimal Backward-Context Model

The decoder should remember the last forward frame that could trigger a backward response.

| Context field        | Example                                                         |
| -------------------- | --------------------------------------------------------------- |
| `last_forward_type`  | `forward16`, `forward24`                                        |
| `last_command`       | `COMPARE`, `QUERY STATUS`, `READ MEMORY LOCATION`               |
| `expects_backward`   | `true/false`                                                    |
| `backward_mode`      | `YES_NO`, `BYTE`, `STATUS_BYTE`, `MEMORY_BYTE`, `SHORT_ADDRESS` |
| `expected_window_ms` | backward-response time window                                   |
| `actual_backward`    | `0xFF`, `0x00`, `0x4C`, none                                    |

Example:

```text
rx_forward16 0xA900
rx_backward  0xFF
```

Decoder:

```text
command = COMPARE
backward_mode = YES_NO
result = YES
```

Example:

```text
rx_forward24 0x01FE3C
rx_backward  0x4C
```

Decoder:

```text
command = READ MEMORY LOCATION
backward_mode = MEMORY_BYTE
result = 0x4C
ascii = 'L'
```

---

## 17. Implementation Status of This Table

The following can already be used safely in the decoder:

```text
- classification of 16/24/8-bit frames,
- forward16 addressing,
- DAPC,
- 102 commands from 0x00 to 0xC5,
- 16-bit special commands,
- DALI-1 commissioning,
- DALI-2 control-device commissioning,
- contextual backward interpretation,
- READ MEMORY LOCATION with ASCII/debug output.
```

One important distinction still remains:

**IEC 62386-103** describes the common mechanism for control devices: addressing, 24-bit frames, device-level commands, instances, memory access, event routing, and so on.

However, **full instance events** are distributed across **IEC 62386-3xx**, such as push buttons, occupancy sensors, light sensors, and similar parts. There is no single universal event table for all instances contained only in 103. The best decoder model is therefore:

```text
forward24
 |- control-device special commands
 |- device-level commands: xx FE yy
 |- instance commands: xx ii yy
 `- input notifications/events: xx ii ee
        `- interpretation depends on instance_type from the matching 3xx part
```

Below is the first 24-bit lookup block: full frame-type separation, the 103 device-level core, the event/instance model, and 3xx dispatch.

---

## 18. DALI-2 / IEC 62386-103 - Lookup for 24-bit Frames

24-bit frame:

```text
raw = 0xAABBCC

byte0 = AA
byte1 = BB
byte2 = CC
```

Standard form:

```text
[ byte0 ][ byte1 ][ byte2 ]
[ addr  ][ target/opcode group ][ opcode/event/data ]
```

In DALI, a forward frame may use 16, 24, or 32 data bits, while a backward frame uses 8 data bits.

### 18.1 Main classes of 24-bit frames

| Condition                                      | Class                                           | Example    | Meaning                                                           |
| ---------------------------------------------- | ----------------------------------------------- | ---------- | ----------------------------------------------------------------- |
| `byte0 == 0xC1`                                | Special command / commissioning control devices | `0xC10300` | Discovery, randomise, compare, short address for control devices  |
| `byte1 == 0xFE`                                | Device-level command/query                      | `0x01FE30` | Command to the whole control device                               |
| `byte1 != 0xFE` and sent by controller         | Instance command                                | `0x0101xx` | Command to specific instance                                      |
| `byte1 != 0xFE` and sent by input device       | Event / input notification                      | `0x01018D` | Event from instance, e.g. button/sensor                           |
| `byte0 == 0xFF` and `byte1 == 0xFE`            | Broadcast device-level                          | `0xFFFE1D` | Broadcast to all control devices                                  |
| `byte0 == 0xFF` and `byte1 != 0xFE`            | Broadcast / special instance-related            | `0xFF01xx` | Context-dependent                                                 |
| `byte0 == 0xC9`                                | Special / memory / extended helper              | `0xC9FFFF` | Requires separate handling as special 103                         |
| other `0xC?xxxx`                               | Special command space                           | `0xC1308F` | DTR / configuration / helper                                      |

---

## 19. Addressing Control Devices in forward24

### 19.1 Short-address encoding

For a control-device short address:

```text
byte0 = (short_address << 1) | 1
```

| Short address | `byte0` |
| ------------- | ------- |
| `0`           | `0x01`  |
| `1`           | `0x03`  |
| `2`           | `0x05`  |
| `3`           | `0x07`  |
| `63`          | `0x7F`  |

Example:

```text
0x01FE30
```

Decoding:

```text
byte0 = 0x01 -> short address 0
byte1 = 0xFE -> device-level command
byte2 = 0x30 -> opcode 0x30
```

### 19.2 Broadcast

| `byte0`                | Meaning                                                                  |
| ---------------------- | ------------------------------------------------------------------------ |
| `0xFF`                 | Broadcast to control devices                                             |
| `0xFD` / other special | Depends on group/special addressing; handle in separate table            |

Example from log:

```text
0xFFFE1D
```

Decoding:

```text
byte0 = 0xFF -> broadcast
byte1 = 0xFE -> device-level
byte2 = 0x1D -> opcode 0x1D
```

---

## 20. Device-Level Opcode Table - IEC 62386-103 Core

These commands mirror classic commissioning for control gear, but apply to control devices and use 24-bit frames.

| Opcode      | Name / role                                  | Type          | Backward mode           | Send twice    | Decoder notes                                  |
| ----------- | -------------------------------------------- | ------------- | ----------------------- | ------------- | ---------------------------------------------- |
| `0x00`      | RESET                                        | Instruction   | None                    | Yes           | Reset control device / device-level parameters |
| `0x01`      | IDENTIFY DEVICE                              | Instruction   | None                    | No            | Physical identification mode                   |
| `0x02`      | RESET POWER CYCLE SEEN                       | Instruction   | None                    | Yes           | Clear power-cycle flag                         |
| `0x03-0x0F` | Reserved / not implemented                   | -             | -                       | -             | Show as reserved                               |
| `0x10`      | SET SHORT ADDRESS / device config command    | Instruction   | None                    | Yes / context | Exact meaning depends on 103 table             |
| `0x11`      | ENABLE APPLICATION CONTROLLER / config       | Instruction   | None                    | Yes / context | Validate against 103                           |
| `0x12`      | DISABLE APPLICATION CONTROLLER / config      | Instruction   | None                    | Yes / context | Validate against 103                           |
| `0x13`      | SET OPERATING MODE / config                  | Instruction   | None                    | Yes           | Value usually from DTR0                        |
| `0x14`      | SET EVENT PRIORITY / event config            | Instruction   | None                    | Yes           | Seen in logs after `C130FF`                    |
| `0x15`      | ENABLE INSTANCE / instance config            | Instruction   | None                    | Yes           | Validate against 103                           |
| `0x16`      | DISABLE INSTANCE / instance config           | Instruction   | None                    | Yes           | Validate against 103                           |
| `0x17`      | SET PRIMARY INSTANCE GROUP                   | Instruction   | None                    | Yes           | Value from DTR0                                |
| `0x18`      | SET INSTANCE GROUP 1                         | Instruction   | None                    | Yes           | Value from DTR0                                |
| `0x19`      | SET INSTANCE GROUP 2                         | Instruction   | None                    | Yes           | Value from DTR0                                |
| `0x1A`      | SET EVENT SCHEME                             | Instruction   | None                    | Yes           | Value from DTR0                                |
| `0x1B`      | SET EVENT FILTER                             | Instruction   | None                    | Yes           | Seen in logs                                   |
| `0x1C`      | RESET EVENT FILTER / set event config        | Instruction   | None                    | Yes           | Seen in logs                                   |
| `0x1D`      | ENABLE DEVICE / ENABLE EVENTS / config       | Instruction   | None                    | Yes           | Seen in logs                                   |
| `0x1E`      | DISABLE DEVICE / DISABLE EVENTS / config     | Instruction   | None                    | Yes           | Seen in logs                                   |
| `0x1F`      | Reserved / implementation-specific           | -             | -                       | -             | Check against 103                              |
| `0x20-0x2F` | Configuration instructions                   | Instruction   | None / opcode-dependent | Usually yes   | Fill from exact 103 table                      |
| `0x30`      | QUERY CONTROL DEVICE STATUS                  | Query         | Status byte             | No            | Seen in logs: `0x01FE30 -> 0x22`               |
| `0x31`      | QUERY DEVICE GROUPS 0-7 / config state       | Query         | Bitmap byte             | No            | Validate against 103                           |
| `0x32`      | QUERY DEVICE GROUPS 8-15 / config state      | Query         | Bitmap byte             | No            | Validate against 103                           |
| `0x33`      | QUERY OPERATING MODE                         | Query         | Byte                    | No            |                                                |
| `0x34`      | QUERY MANUFACTURER SPECIFIC MODE / state     | Query         | Byte                    | No            |                                                |
| `0x35`      | QUERY VERSION NUMBER                         | Query         | Byte                    | No            |                                                |
| `0x36`      | QUERY NUMBER OF INSTANCES                    | Query         | Byte                    | No            |                                                |
| `0x37`      | QUERY CONTENT DTR0                           | Query         | Byte                    | No            |                                                |
| `0x38`      | QUERY CONTENT DTR1 / DTR2                    | Query         | Byte                    | No            | Needs validation                               |
| `0x39`      | QUERY RANDOM ADDRESS H                       | Query         | Byte                    | No            | Seen in logs: `0x01FE39 -> 0x2B`               |
| `0x3A`      | QUERY RANDOM ADDRESS M                       | Query         | Byte                    | No            | Seen in logs: `0x01FE3A -> 0xF4`               |
| `0x3B`      | QUERY RANDOM ADDRESS L                       | Query         | Byte                    | No            | Seen in logs: `0x01FE3B -> 0xF6`               |
| `0x3C`      | READ MEMORY LOCATION                         | Query         | Memory byte             | No            | Seen in logs: `0x01FE3C -> ASCII/data`         |
| `0x3D-0x7F` | Reserved / 103-specific query space          | -             | -                       | -             | Do not guess names without 103 table           |
| `0x80-0xFF` | Extended / instance-type / application space | Contextual    | command-dependent       | Depends       | Dispatch to 3xx or extension                   |

Implementation note: for opcode `0x10-0x2F` and part of `0x31-0x38`, the labels are intentionally conservative. The names should be validated line by line against the exact IEC 62386-103 revision so the decoder does not present incorrect command names.

---

### 20.1 `QUERY CONTROL DEVICE STATUS` - `xx FE 30`

Format:

```text
xx FE 30
```

Example:

```text
0x01FE30 -> rx_backward 0x22
```

Response-bit table - decoder model:

| Bit | Mask   | Working meaning                              |
| --- | ------ | -------------------------------------------- |
| 0   | `0x01` | input-device error / device failure          |
| 1   | `0x02` | power cycle seen                             |
| 2   | `0x04` | reset state                                  |
| 3   | `0x08` | missing short address                        |
| 4   | `0x10` | application-controller error / device state  |
| 5   | `0x20` | instance-related status / device active      |
| 6   | `0x40` | reserved / implementation-specific           |
| 7   | `0x80` | reserved / implementation-specific           |

For the decoder, the safe baseline is:

```text
0x01FE30 -> status byte
do not treat 0xFF only as YES
```

### 20.2 `READ MEMORY LOCATION` - `xx FE 3C`

Format:

```text
xx FE 3C
```

It requires a memory pointer set through DTR:

```text
C131bb -> bank / DTR1
C130aa -> address / DTR0
xxFE3C -> read memory location
```

Example from log:

```text
C13100
C1308F
01FE3C -> 0x05
01FE3C -> 0x27
01FE3C -> 0x3D
01FE3C -> 0xBA
01FE3C -> 0x2D
01FE3C -> 0x49
01FE3C -> 0x4E
01FE3C -> 0x54
...
```

ASCII fragment:

```text
2D 49 4E 54 2D 41 51 2D 4C 45 2D 57 31 36
= "-INT-AQ-LE-W16"
```

For the decoder:

| Condition                 | Interpretation                                                  |
| ------------------------- | --------------------------------------------------------------- |
| Previous command `xxFE3C` | backward = data byte                                            |
| Byte `0x20-0x7E`          | optionally display ASCII                                        |
| Byte `0x00`               | terminator / padding / data value by memory-bank context        |
| No backward               | no data / device did not respond / invalid address              |

### 20.3 Instance Commands: `xx ii yy`

Format:

```text
[ address ][ instance ][ opcode ]
```

Abstract example:

```text
0x01018C
```

Decoding:

```text
address  = 0x01 -> short address 0
instance = 0x01
opcode/event = 0x8C
```

### 20.4 How to Distinguish an Instance Command from an Event

This is critical for the sniffer.

| Criterion         | Instance command             | Event / input notification       |
| ----------------- | ---------------------------- | -------------------------------- |
| Sender            | application controller       | input device                     |
| Expects backward  | sometimes                    | no                               |
| `byte1`           | instance number              | instance number                  |
| `byte2`           | instance-command opcode      | event information                |
| Timing            | usually controller-driven    | may appear asynchronously        |
| Example           | `controller -> 0x0101xx`     | `sensor -> 0x01018D`             |

If the sniffer does not know the physical sender direction, apply this heuristic:

```text
if byte1 != 0xFE
and byte2 falls in event range
and no backward follows
and the frame appears asynchronously,
classify it as input notification / event.
```

## 21. Event Dispatch by Instance Type - 3xx

| Instance type | IEC part      | Instance type name           | Event decoding strategy            |
| ------------- | ------------- | ---------------------------- | ---------------------------------- |
| `0x01`        | IEC 62386-301 | Push button / input switch   | Push-button events                 |
| `0x02`        | IEC 62386-302 | Absolute input               | Absolute value / level             |
| `0x03`        | IEC 62386-303 | Occupancy sensor             | Occupancy events                   |
| `0x04`        | IEC 62386-304 | Light sensor                 | Light-level events / values        |
| `0x05`        | IEC 62386-305 | Colour sensor                | Colour-related events / values     |
| `0x06`        | IEC 62386-306 | General purpose sensor       | Generic sensor events              |
| `0x07`        | IEC 62386-307 | Thermal sensor / temperature | Thermal / temperature events       |
| `0x08+`       | later 3xx     | Other types                  | Requires table from matching part  |

---

## 22. Event Schemes

In 103, an event may be encoded using different schemes. That means `0x8C` alone is not always enough without knowing event-scheme configuration.

For the decoder, keep per-instance:

```text
instance_type
event_scheme
event_filter
event_priority
instance_group
```

| Event scheme               | Event contents                           | Decoder consequence              |
| -------------------------- | ---------------------------------------- | -------------------------------- |
| Device/instance addressing | Device address + instance number + event | Easiest to decode                |
| Device group addressing    | Device group + instance + event          | Requires group map               |
| Instance group addressing  | Instance group + event                   | Requires instance-group config   |
| Broadcast event            | Event without unique device/instance     | Treat carefully                  |

---

## 23. Typical 3xx Event Families

### 23.1 IEC 62386-301 - Push-button instance events

| Event code   | Event name                        | Meaning                         | Backward |
| ------------ | --------------------------------- | ------------------------------- | -------- |
| `0x00`       | Button released                   | Button released                 | No       |
| `0x01`       | Button pressed                    | Button pressed                  | No       |
| `0x02`       | Short press                       | Short press                     | No       |
| `0x03`       | Double press                      | Double press                    | No       |
| `0x04`       | Long press start                  | Start of long press             | No       |
| `0x05`       | Long press repeat                 | Long-press repeat               | No       |
| `0x06`       | Long press stop                   | End of long press               | No       |
| `0x07`       | Button free                       | Button released from blocked/free state | No |
| `0x08`       | Button stuck                      | Button stuck                    | No       |
| `0x09-0x7F`  | Reserved / vendor-specific        | Unknown                         | No       |
| `0x80-0xFF`  | Encoded event / scheme-dependent  | Depends on event scheme         | No       |

### 23.2 IEC 62386-302 - Absolute input events

| Event information | Meaning                           | Backward | Notes                                |
| ----------------- | --------------------------------- | -------- | ------------------------------------ |
| `0x00-0xFE`       | Encoded absolute value            | No       | Depends on instance resolution       |
| `0xFF`            | MASK / invalid / no value         | No       | Context-dependent                    |
| scheme-dependent  | Multi-byte / filtered value event | No       | Requires instance configuration      |

### 23.3 IEC 62386-303 - Occupancy sensor events

| Event code   | Meaning                        | Backward |
| ------------ | ------------------------------ | -------- |
| `0x00`       | No movement / vacant           | No       |
| `0x01`       | Movement / occupied            | No       |
| `0x02`       | Still vacant                   | No       |
| `0x03`       | Still occupied                 | No       |
| `0x04-0x7F`  | Reserved / sensor-specific     | No       |
| `0x80-0xFF`  | Scheme-dependent encoded event | No       |

### 23.4 IEC 62386-304 - Light sensor events

| Event information | Meaning                           | Backward | Notes                              |
| ----------------- | --------------------------------- | -------- | ---------------------------------- |
| `0x00-0xFE`       | Encoded illuminance / light level | No       | Requires scale/resolution          |
| `0xFF`            | invalid / MASK / no value         | No       | Context-dependent                  |
| scheme-dependent  | Filtered / threshold event        | No       | Requires 304 configuration         |

### 23.5 IEC 62386-305 - Colour Sensor Events

| Event information | Meaning                      | Backward | Notes                                  |
| ----------------- | ---------------------------- | -------- | -------------------------------------- |
| `0x00-0xFE`       | Encoded colour-related value | No       | Value type depends on configuration    |
| `0xFF`            | invalid / MASK               | No       | Context-dependent                      |
| scheme-dependent  | Tc / xy / RGBW / channel-dependent | No   | Requires detailed 305 table            |

### 23.6 IEC 62386-306 - General Purpose Sensor Events

| Event information | Meaning                      | Backward | Notes                         |
| ----------------- | ---------------------------- | -------- | ----------------------------- |
| `0x00-0xFE`       | Encoded sensor value         | No       | Generic value                 |
| `0xFF`            | invalid / MASK               | No       | Context-dependent             |
| scheme-dependent  | Sensor-type-specific value   | No       | Requires 306 configuration    |

### 23.7 IEC 62386-307 - Thermal / Temperature Sensor Events

| Event information | Meaning                              | Backward | Notes                      |
| ----------------- | ------------------------------------ | -------- | -------------------------- |
| `0x00-0xFE`       | Encoded temperature / thermal value  | No       | Scale depends on 307       |
| `0xFF`            | invalid / MASK                       | No       | Context-dependent          |
| scheme-dependent  | Alert / threshold / value            | No       | Requires 307 configuration |

---

## 24. Exact 24-bit Frame Classification Algorithm

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

## 25. Sniffer Heuristics Without Sender Direction

| Situation                                                      | Classification                   |
| -------------------------------------------------------------- | -------------------------------- |
| `b0 == 0xC1`                                                   | Special commissioning            |
| `b1 == 0xFE`                                                   | Device-level command/query       |
| `b1 != 0xFE`, backward follows                                 | Instance query/command           |
| `b1 != 0xFE`, no backward, frame appears asynchronously        | Event/input notification         |
| `b2` in common event range for known `instance_type`           | Event                            |
| `b2` known as instance opcode                                  | Instance command                 |
| No context                                                     | Show as `instance/event ambiguous` |

---

## 26. Minimal State the Decoder Should Remember

| Field                           | Why it is needed                               |
| ------------------------------- | ---------------------------------------------- |
| `device_short_address`          | Decode `byte0`                                 |
| `device_groups`                 | Group event schemes                            |
| `number_of_instances`           | Validate `byte1`                               |
| `instance_type[instance]`       | Dispatch into 3xx                              |
| `event_scheme[instance]`        | Decode event correctly                         |
| `event_filter[instance]`        | Explain why an event appears / does not appear |
| `event_priority[instance]`      | Event priority                                 |
| `memory_bank`, `memory_address` | Interpret `READ MEMORY LOCATION`               |
| `last_forward_expects_backward` | Interpret `rx_backward`                        |

---

## 27. Examples from Your Logs

### 27.1 Control-device commissioning

```text
0xC105FF
0xC106FF
0xC107FF
0xC10300
rx_backward 0xFF
```

Decoder:

```text
SEARCHADDR = 0xFFFFFF
COMPARE = YES
```

### 27.2 Found random address

```text
0xC1053D
0xC10616
0xC10740
```

Decoder:

```text
random/search address = 0x3D1640
```

### 27.3 Programming short address

```text
0xC10800
0xC10A00
rx_backward 0x00
0xC10400
```

Decoder:

```text
PROGRAM SHORT ADDRESS
QUERY SHORT ADDRESS -> 0x00
WITHDRAW
```

### 27.4 Query random address

```text
0x01FE39 -> 0x2B
0x01FE3A -> 0xF4
0x01FE3B -> 0xF6
```

Decoder:

```text
QUERY RANDOM ADDRESS H/M/L
random address = 0x2BF4F6
```

### 27.5 Read memory ASCII

```text
0x01FE3C -> 0x4C
0x01FE3C -> 0x75
0x01FE3C -> 0x6E
0x01FE3C -> 0x61
```

Decoder:

```text
READ MEMORY LOCATION
bytes = 4C 75 6E 61
ASCII = "Luna"
```

---

## 28. Important Limitation of This Lookup Version

This table is ready as a **24-bit DALI-2 / 103 decoder scaffold**, but it should not yet be treated as normatively complete for all `3xx` behaviors, because:

```text
- 3xx events depend on the specific instance type,
- different 301/302/303/... parts define their own event tables,
- 103 alone is not enough for full interpretation of buttons, occupancy, light sensors, and similar devices,
- part of the device-level opcode range 0x10-0x2F still needs line-by-line validation against the exact IEC 62386-103 revision.
```

The safest current implementation path for the sniffer is:

```text
1. Decode the frame class correctly.
2. Decode the known core opcodes: C1xxxx, C130/C131/C132, xxFE30, xxFE39/3A/3B, xxFE3C.
3. For remaining xxFEyy values, show:
   - opcode,
   - type: device-level instruction/query,
   - expected backward: yes/no when known,
   - status: requires IEC 62386-103 opcode-table verification.
4. For events xx ii ee, dispatch through:
   - device,
   - instance,
   - raw event,
   - instance type,
   - 3xx interpretation when known.
```

This prevents the decoder from assigning incorrect names to frames, which would be worse than presenting them as `known class / unknown opcode`.

---

## 29. Additional Forward24 Classification for DALI-2 Sensor Frames

This section extends the 24-bit decoder to handle frames originating from DALI-2 input devices such as sensors, push buttons, input panels, and multisensors.

Important assumption:

```text
A DALI-2 sensor / input device may itself transmit a 24-bit forward frame as an event/input notification.
This is not a backward frame.
Backward frames still use 8 bits.
```

24-bit frame format:

```text
raw = 0xAABBCC

byte0 = AA
byte1 = BB
byte2 = CC
```

General interpretation for instance-related frames:

```text
[ byte0 ][ byte1 ][ byte2 ]
[ source/address ][ instance ][ event information / opcode ]
```

---

## 30. Forward24 Classification Priority

The decoder should classify 24-bit frames in a fixed order. This matters because some special frames, such as `0xC9FFFF`, may otherwise be incorrectly classified as instance events if fallback runs too early.

| Priority | Condition                                                                                     | Decoder class                         | Meaning                                          |
| -------: | --------------------------------------------------------------------------------------------- | ------------------------------------- | ------------------------------------------------ |
| 1        | `byte0 == 0xC1`                                                                               | `forward24_control_device_special`    | Special commands / commissioning control devices |
| 2        | `byte0 >= 0xC0 && byte0 <= 0xCF`                                                              | `forward24_special_or_helper`         | DTR, memory helper, special 103 command space    |
| 3        | `byte1 == 0xFE`                                                                               | `forward24_device_level_command`      | Device-level command/query: `xx FE yy`           |
| 4        | `byte0 == 0xFF && byte1 == 0xFE`                                                              | `forward24_broadcast_device_level`    | Broadcast device-level command                   |
| 5        | `byte0` is a valid short address, `byte1 != 0xFE`, and no backward follows                    | `forward24_input_notification`        | Instance event/input notification                |
| 6        | `byte0` is a valid short address, `byte1 != 0xFE`, and backward follows                       | `forward24_instance_command_or_query` | Instance command/query                           |
| 7        | everything else                                                                               | `forward24_unknown_or_ambiguous`      | Unknown or incomplete interpretation             |

Implementation rule:

```text
Do not classify frames in the 0xC0xxxx-0xCFxxxx range as instance events.
This range must be handled earlier as special/helper space.
```

---

## 31. Forward24 Input Notification / Instance Event

Class:

```text
forward24_input_notification
```

Format:

```text
[ source address ][ instance number ][ event information ]
```

| Field               | Meaning                                        |
| ------------------- | ---------------------------------------------- |
| `byte0`             | source control-device address                  |
| `byte1`             | instance number                                |
| `byte2`             | event information / event code                 |
| Backward expected   | `false`                                        |
| Frame type          | 24-bit forward                                 |
| Logical direction   | input device / sensor -> bus                   |
| Standard area       | IEC 62386-103 + matching IEC 62386-3xx part    |

Example:

```text
raw = 0x01018D

byte0 = 0x01
byte1 = 0x01
byte2 = 0x8D
```

Decoding:

```text
frame_class: forward24_input_notification
source_short_address: 0
instance: 1
event_info: 0x8D
backward_expected: false
semantic_decode: requires instance_type from IEC 62386-3xx
```

---

## 32. Source-Address Decoding for Input Notifications

For a typical source event from a short-addressed device:

```text
byte0 = (short_address << 1) | 1
```

Decoder:

```text
if (byte0 & 0x01) == 1 and byte0 <= 0x7F:
    short_address = byte0 >> 1
```

Examples:

| `byte0` | Decoding           |
| ------: | ------------------ |
| `0x01`  | short address `0`  |
| `0x03`  | short address `1`  |
| `0x05`  | short address `2`  |
| `0x7F`  | short address `63` |

Example from log:

```text
0x01018C
```

Decoding:

```text
byte0 = 0x01 -> short address 0
byte1 = 0x01 -> instance 1
byte2 = 0x8C -> event information 0x8C
```

---

## 33. Basic Interpretation of Input Notifications

If the decoder does not yet know the instance type, it should not mark the frame as `ambiguous`. It should still present it as a correctly recognized generic event.

Recommended presentation:

```text
Name: INPUT NOTIFICATION
Status: decoded_generic
Confidence: 75-85%
Backward expected: no
```

Parameters:

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

Incorrect presentation:

```text
INSTANCE COMMAND / EVENT
Status: ambiguous
Confidence: 45%
```

Correct presentation:

```text
INPUT NOTIFICATION
Status: decoded_generic
Confidence: 80%
```

---

## 34. Correlation with Backward Frames

`forward24_input_notification` frames do not expect backward responses.

Rule:

```text
If frame_class == forward24_input_notification:
    expects_backward = false
```

That means the absence of `rx_backward` after frames such as:

```text
0x01018C
0x01018D
```

is not an error.

| Frame class                                             | Expects backward?        |
| ------------------------------------------------------- | ------------------------ |
| `forward24_device_level_command`                        | depends on opcode        |
| `forward24_control_device_special COMPARE`              | yes, `0xFF` or none      |
| `forward24_control_device_special QUERY SHORT ADDRESS`  | yes, byte or none        |
| `forward24_input_notification`                          | no                       |
| `forward24_instance_command_or_query`                   | depends on opcode        |

---

## 35. Distinguishing Instance Commands from Input Notifications

The same byte layout:

```text
[ address ][ instance ][ payload ]
```

may represent either a command/query or an event. The distinction depends on context.

| Criterion | Instance command/query             | Input notification/event |
| --------- | ---------------------------------- | ------------------------ |
| Sender    | application controller             | control device / sensor  |
| Backward  | may occur                          | does not occur           |
| Timing    | usually part of controller traffic | often asynchronous       |
| `byte1`   | instance number                    | instance number          |
| `byte2`   | opcode / parameter                 | event information        |
| UI class  | `INSTANCE COMMAND/QUERY`           | `INPUT NOTIFICATION`     |

Heuristic for a sniffer without physical sender information:

```text
if byte1 != 0xFE
and byte0 is a valid short-addressed source
and no backward follows in the response window
and the frame is not in special/helper range:
    classify as forward24_input_notification
```

---

## 36. Instance Context Required for Full Event Decoding

`event_info = 0x8D` alone is not enough for a full semantic description.

The decoder should maintain per-device context:

| Context field         | Source of information           | Purpose                                |
| --------------------- | ------------------------------- | -------------------------------------- |
| `short_address`       | commissioning / scan            | device identification                  |
| `number_of_instances` | device-level query              | validate instance number               |
| `instance_type[n]`    | instance query / memory bank    | dispatch to correct 3xx part           |
| `event_scheme[n]`     | instance configuration          | interpret event format                 |
| `event_filter[n]`     | instance configuration          | determine which events are active      |
| `event_priority[n]`   | configuration                   | event priority                         |
| `instance_group[n]`   | configuration                   | event routing / instance groups        |

If `instance_type` is unknown:

```text
Do not guess the meaning of the event.
Show it as a generic input notification.
```

---

## 37. Event Dispatch by Instance Type

Once the instance type is known, the decoder should pass `event_info` into the matching 3xx decoder.

| Instance type | IEC part      | Instance type name             | Event decoder                                 |
| ------------: | ------------- | ------------------------------ | --------------------------------------------- |
| `0x01`        | IEC 62386-301 | Push button                    | `decode_301_push_button_event(event_info)`    |
| `0x02`        | IEC 62386-302 | Absolute input                 | `decode_302_absolute_input_event(event_info)` |
| `0x03`        | IEC 62386-303 | Occupancy sensor               | `decode_303_occupancy_event(event_info)`      |
| `0x04`        | IEC 62386-304 | Light sensor                   | `decode_304_light_event(event_info)`          |
| `0x05`        | IEC 62386-305 | Colour sensor                  | `decode_305_colour_event(event_info)`         |
| `0x06`        | IEC 62386-306 | General purpose sensor         | `decode_306_gp_sensor_event(event_info)`      |
| `0x07`        | IEC 62386-307 | Thermal / temperature sensor   | `decode_307_thermal_event(event_info)`        |
| unknown       | -             | Unknown instance type          | show raw event information                    |

Fallback:

```text
INPUT NOTIFICATION
instance_type: unknown
event_info: 0x8D
semantic_name: unavailable
```

---

## 38. Event Scheme and Its Impact on Interpretation

DALI-2 control devices may use different event schemes. The decoder should therefore separate:

```text
recognizing a frame as an event
```

from:

```text
assigning a semantic event name
```

| Decode level           | Required context                                      | Example result                                             |
| ---------------------- | ----------------------------------------------------- | ---------------------------------------------------------- |
| Generic frame decode   | only raw 24-bit                                       | `INPUT NOTIFICATION, short:0, instance:1, event_info:0x8D` |
| Instance-aware decode  | known `instance_type`                                 | `Push button event 0x8D` or `Occupancy event 0x8D`         |
| Full semantic decode   | `instance_type`, `event_scheme`, `event_filter` known | exact event name defined by matching 3xx part              |

If the event scheme is unknown:

```text
status: decoded_generic
warning: event scheme unknown
```

---

## 39. Examples of Sensor-Event Decoding

### 39.1 Event `0x01018C`

Raw:

```text
0x01018C
```

Decoding:

```text
byte0 = 0x01
byte1 = 0x01
byte2 = 0x8C
```

Result:

```text
frame_class: forward24_input_notification
name: INPUT NOTIFICATION
source_short_address: 0
instance: 1
event_info: 0x8C
backward_expected: false
status: decoded_generic
```

### 39.2 Event `0x01018D`

Raw:

```text
0x01018D
```

Decoding:

```text
byte0 = 0x01
byte1 = 0x01
byte2 = 0x8D
```

Result:

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

## 40. Special/Helper Range - Preventing Misclassification

Frames in the range:

```text
0xC0xxxx-0xCFxxxx
```

must not be automatically classified as instance events.

Problematic example:

```text
0xC9FFFF
```

Incorrect:

```text
INSTANCE COMMAND / EVENT
status: ambiguous
```

Correct:

```text
forward24_special_or_helper
status: decoded_class_only
```

Rule:

```text
if byte0 >= 0xC0 and byte0 <= 0xCF:
    classify as forward24_special_or_helper
    stop generic instance/event fallback
```

Specific exception:

```text
byte0 == 0xC1
```

should already be decoded earlier as:

```text
forward24_control_device_special
```

that is, commissioning for control devices.

---

## 41. Device-Level Command vs Input Notification

Device-level frames always have:

```text
byte1 == 0xFE
```

Example:

```text
0x01FE30
```

Decoding:

```text
byte0 = 0x01 -> short address 0
byte1 = 0xFE -> device-level command/query
byte2 = 0x30 -> opcode
```

Class:

```text
forward24_device_level_command
```

By contrast, frames:

```text
0x01018C
0x01018D
```

have:

```text
byte1 = 0x01
```

so they are not device-level commands. They are instance-related frames:

```text
source short address 0
instance 1
payload/event_info 0x8C / 0x8D
```

If there is no backward and the frame is not part of controller traffic, classify it as:

```text
forward24_input_notification
```

---

## 42. Proposed Pseudocode for Forward24

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

## 43. Helper Function: Valid Short-Address Byte

```text
function is_valid_short_address_byte(byte0):
    return ((byte0 & 0x01) == 1) and (byte0 <= 0x7F)
```

Examples:

| `byte0` | Result                                       | Meaning                     |
| ------: | -------------------------------------------- | --------------------------- |
| `0x01`  | valid                                        | short address 0             |
| `0x03`  | valid                                        | short address 1             |
| `0x7F`  | valid                                        | short address 63            |
| `0x00`  | invalid for command-source short addressing  | selector bit = 0            |
| `0x80`  | invalid for short source                     | outside short-address range |
| `0xC1`  | invalid here                                 | special command range       |
| `0xFF`  | invalid here                                 | broadcast/special           |

---

## 44. Recommended UI Output for Input Notifications

For frame:

```text
0x01018D
```

the UI should display:

| Field               | Value                                                            |
| ------------------- | ---------------------------------------------------------------- |
| Raw                 | `0x01018D`                                                       |
| Direction           | `rx_forward24`                                                   |
| Name                | `INPUT NOTIFICATION`                                             |
| Status              | `decoded_generic`                                                |
| Frame class         | `forward24_input_notification`                                   |
| Addressing          | `short:0`                                                        |
| Instance            | `1`                                                              |
| Event information   | `0x8D`                                                           |
| Backward expected   | `false`                                                          |
| Confidence          | `80%`                                                            |
| Note                | `Semantic event name requires instance type from IEC 62386-3xx`  |

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

## 45. Confidence Rule for Forward24 Input Notifications

| Condition                                                                                 | Confidence                     |
| ----------------------------------------------------------------------------------------- | -----------------------------: |
| Valid `byte0` as short address, `byte1 != 0xFE`, no backward, not in special range       | `80%`                          |
| Plus known `instance_type` for that instance                                              | `90%`                          |
| Plus known `event_scheme`                                                                 | `95%`                          |
| Unknown `instance_type`, but frame appears asynchronously                                 | `80%`                          |
| Unknown sender direction and controller commands are nearby                               | `60-70%`                       |
| `byte0` in the `0xC0-0xCF` range                                                          | do not classify as event       |

---

## 46. Test Vectors for the Decoder

| Raw        | Expected class                      | Name                                 | Params                                     | Backward expected                |
| ---------- | ----------------------------------- | ------------------------------------ | ------------------------------------------ | -------------------------------- |
| `0x01018C` | `forward24_input_notification`      | `INPUT NOTIFICATION`                 | `short:0`, `instance:1`, `event_info:0x8C` | `false`                          |
| `0x01018D` | `forward24_input_notification`      | `INPUT NOTIFICATION`                 | `short:0`, `instance:1`, `event_info:0x8D` | `false`                          |
| `0x01FE30` | `forward24_device_level_command`    | device-level opcode `0x30`           | `short:0`, `opcode:0x30`                   | depends on opcode                |
| `0x01FE3C` | `forward24_device_level_command`    | `READ MEMORY LOCATION`               | `short:0`, `opcode:0x3C`                   | `true`, byte                     |
| `0xC10300` | `forward24_control_device_special`  | `COMPARE`                            | none                                       | `true`, yes/no                   |
| `0xC105FF` | `forward24_control_device_special`  | `SEARCHADDRH`                        | `0xFF`                                     | `false`                          |
| `0xC9FFFF` | `forward24_special_or_helper`       | special/helper unknown               | `byte0:0xC9`                               | context-dependent                |
| `0xFFFE1D` | `forward24_broadcast_device_level`  | broadcast device-level opcode `0x1D` | `broadcast`, `opcode:0x1D`                 | usually false / opcode-dependent |

---

## 47. Known Limitation - Semantic Event Decoding

At this stage the decoder can correctly recognize:

```text
INPUT NOTIFICATION
source short address
instance
event information
```

but it cannot always correctly name the event as, for example:

```text
button pressed
presence detected
light level changed
temperature event
```

That requires:

```text
instance_type
event_scheme
the IEC 62386-3xx part matching the given instance
```

Therefore the recommended fallback is:

```text
INPUT NOTIFICATION / semantic event unknown
```

instead of:

```text
ambiguous
```

---

## 48. Minimal Decoder Change Required

To stop sensor frames from falling into `ambiguous`, it is enough to add:

```text
1. Priority exclusion for the 0xC0xxxx-0xCFxxxx range.
2. A dedicated `forward24_input_notification` class.
3. Rule:
   if byte0 is a valid short address
   and byte1 != 0xFE
   and no backward follows
   then INPUT NOTIFICATION.
4. Semantic fallback:
   if instance_type unknown -> decoded_generic, not ambiguous.
```

Example result for your case:

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
