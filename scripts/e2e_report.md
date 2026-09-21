# E2E UCI Report

Datasets: 13 | PASS: 12, PARTIAL: 0, FAIL: 0, SKIP: 1 | total 43s

| id | status | problem | raw (rows×feat) | clean (rows×feat) | placeholders→NA | imputed | cols dropped | encodings | time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 53 | **PASS** | Classification | 150×4 | 147×4 | 0 | 0 | [] | One-Hot Encoding ✓0.9333<br>Target Encoding ✓0.9333<br>Leave-One-Out Encoding ✓0.9333<br>M-Estimate Encoding ✓0.9333 | 1.8s+0.0s+0.4s |
| 109 | **PASS** | Classification | 178×13 | 178×13 | 0 | 0 | [] | One-Hot Encoding ✓1.0<br>Target Encoding ✓1.0<br>Leave-One-Out Encoding ✓1.0<br>M-Estimate Encoding ✓1.0 | 1.8s+0.0s+0.4s |
| 2 | **PASS** | Classification | 48842×14 | 48753×14 | 4262 | 6465 | [] | One-Hot Encoding ✓0.803<br>Target Encoding ✓0.8003<br>Leave-One-Out Encoding ✓0.801<br>M-Estimate Encoding ✓0.8009 | 4.3s+2.4s+2.0s |
| 45 | **PASS** | Classification | 303×13 | 303×13 | 0 | 6 | [] | One-Hot Encoding ✓0.541<br>Target Encoding ✓0.541<br>Leave-One-Out Encoding ✓0.541<br>M-Estimate Encoding ✓0.541 | 1.8s+0.0s+0.5s |
| 73 | **PASS** | Classification | 8124×22 | 8124×21 | 0 | 2480 | ['veil-type'] | One-Hot Encoding ✓0.9988<br>Target Encoding ✓0.9957<br>Leave-One-Out Encoding ✓0.9975<br>M-Estimate Encoding ✓0.9969 | 2.8s+1.1s+1.0s |
| 27 | **PASS** | Classification | 690×15 | 690×15 | 0 | 67 | [] | One-Hot Encoding ✓0.8188<br>Target Encoding ✓0.8188<br>Leave-One-Out Encoding ✓0.7971<br>M-Estimate Encoding ✓0.8333 | 2.1s+0.1s+0.5s |
| 159 | **PASS** | Classification | 19020×10 | 18905×10 | 0 | 0 | [] | One-Hot Encoding ✓0.7887<br>Target Encoding ✓0.7887<br>Leave-One-Out Encoding ✓0.7887<br>M-Estimate Encoding ✓0.7887 | 3.3s+0.1s+0.5s |
| 275 | **PASS** | Regression | 17379×13 | 17379×13 | 0 | 0 | [] | One-Hot Encoding ✓0.3884<br>Target Encoding ✓0.3884<br>Leave-One-Out Encoding ✓0.3884<br>M-Estimate Encoding ✓0.3884 | 3.3s+0.1s+0.1s |
| 186 | **PASS** | Classification | 6497×11 | 5314×11 | 0 | 0 | [] | One-Hot Encoding ✓0.3142<br>Target Encoding ✓0.3142<br>Leave-One-Out Encoding ✓0.3142<br>M-Estimate Encoding ✓0.3142 | 2.7s+0.0s+1.0s |
| 17 | **PASS** | Classification | 569×30 | 569×30 | 0 | 0 | [] | One-Hot Encoding ✓0.9825<br>Target Encoding ✓0.9825<br>Leave-One-Out Encoding ✓0.9825<br>M-Estimate Encoding ✓0.9825 | 2.5s+0.0s+0.4s |
| 12 | **PASS** | Classification | 625×4 | 625×4 | 0 | 0 | [] | One-Hot Encoding ✓0.928<br>Target Encoding ✓0.928<br>Leave-One-Out Encoding ✓0.928<br>M-Estimate Encoding ✓0.928 | 1.8s+0.0s+0.4s |
| 46 | **PASS** | Classification | 155×19 | 155×19 | 0 | 167 | [] | One-Hot Encoding ✓0.8065<br>Target Encoding ✓0.8065<br>Leave-One-Out Encoding ✓0.8065<br>M-Estimate Encoding ✓0.8065 | 1.8s+0.0s+0.4s |
| 92 | **SKIP** | Classification | 23×4 | ?×? | - | - | - | skipped | 1.7s |

## id=92 → SKIP

```
500: Error cleaning dataset: Cleaning left a single class in the target. Classification needs at least 2 classes.
```

