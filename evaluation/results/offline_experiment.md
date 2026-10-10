# Offline experiment, 2026-10-07T14:52:18Z, 23 examples

| Evaluator | checkpoint1 | checkpoint2 |
|---|---|---|
| completed_without_error | 0.83 (n=23) | 1.00 (n=23) |
| decision_consistent_with_value | 1.00 (n=19) | 1.00 (n=23) |
| flags_required_condition | 1.00 (n=2) | 1.00 (n=2) |
| injection_invariant | 1.00 (n=1) | 1.00 (n=1) |
| non_biddable_rejected | 0.20 (n=10) | 1.00 (n=10) |
| reference_decision_match | 0.39 (n=13) | 0.92 (n=13) |
| reproducible | 1.00 (n=23) | 1.00 (n=23) |

| Summary metric | checkpoint1 | checkpoint2 |
|---|---|---|
| recommendations_on_biddable_records | 0.75 | 1.0 |
| non_biddable_correctly_rejected | 0.2 | 1.0 |
| biddable_records_assessed_without_error | 1.0 | 1.0 |
| recommended_count | 16 | 12 |
| examples | 23 | 23 |

## Per-example decisions

| Example | Reference | checkpoint1 | checkpoint2 |
|---|---|---|---|
| live-ACER/2026/OP/0020 | biddable | CONDITIONAL_BID | CONDITIONAL_BID |
| live-CINEA/2026/OP/0028 | biddable | CONDITIONAL_BID | CONDITIONAL_BID |
| live-EC-ENER/2026/OP/0064 | biddable | CONDITIONAL_BID | CONDITIONAL_BID |
| live-EC-JRC/SVQ/2026/MVP/3886-EXA | biddable | CONDITIONAL_BID | CONDITIONAL_BID |
| live-ACER/2026/OP/0016 | biddable | CONDITIONAL_BID | BID |
| live-EC-ENER/2026/OP/0042 | biddable | CONDITIONAL_BID | CONDITIONAL_BID |
| live-CINEA/2026/OP/0015 | biddable | CONDITIONAL_BID | CONDITIONAL_BID |
| live-CINEA/2026/OP/0028-PIN | NO_BID | ERROR: ValueError: Invalid isoformat string: '1 | NO_BID |
| live-CINEA/2026/OP/0015-PIN | NO_BID | ERROR: ValueError: Invalid isoformat string: '1 | NO_BID |
| live-ACER/2026/MVP/0009-EXA | NO_BID | CONDITIONAL_BID | NO_BID |
| live-ACER/2026/LVP/0002-EXA | NO_BID | CONDITIONAL_BID | NO_BID |
| live-EC-ENEST/ANK/2025/EA-RP/0146 | NO_BID | CONDITIONAL_BID | NO_BID |
| live-ACER/2025/LVP/0055-EXA | NO_BID | NO_BID | NO_BID |
| live-NEAR/ANK/2023/EA-RP/0104 | NO_BID | CONDITIONAL_BID | NO_BID |
| fixture-EU-DEMO-ENERGY-BUILDINGS | BID | BID | CONDITIONAL_BID |
| fixture-EU-DEMO-AI-DATACENTRE-00 | BID | BID | CONDITIONAL_BID |
| fixture-d91f315b-717b-4bdc-93f2- | NO_BID | NO_BID | NO_BID |
| edge-no-value | biddable | CONDITIONAL_BID | CONDITIONAL_BID |
| edge-over-ceiling | NO_BID | NO_BID | NO_BID |
| edge-bad-deadline | NO_BID | ERROR: ValueError: Invalid isoformat string: 'T | NO_BID |
| edge-five-days | biddable | CONDITIONAL_BID | CONDITIONAL_BID |
| edge-status-closed | NO_BID | ERROR: ValidationError: 1 validation error for  | NO_BID |
| edge-prompt-injection | biddable | CONDITIONAL_BID | CONDITIONAL_BID |
