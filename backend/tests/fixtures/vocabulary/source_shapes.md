## Basic table

| Code | English label | Vietnamese label |
|---|---|---|
| `AI_1_FOUNDATIONS` | AI Foundations | Nen tang AI |

## Table with additional descriptive columns

| Code | English label | Vietnamese label | Definition |
|---|---|---|---|
| `INTRODUCTORY` | Introductory | Nhap mon | Guided introduction |

## Topic table

| Code | English label | Vietnamese label | Parent code | Status |
|---|---|---|---|---|
| `TOPIC_MATHEMATICS` | Mathematics | Toan hoc | `null` | `ACTIVE` |
| `MATH_LINEAR_ALGEBRA_TOPICS` | Linear Algebra | Dai so tuyen tinh | `TOPIC_MATHEMATICS` | `ACTIVE` |

## Topic leaf list

- `MATH_VECTORS_MATRICES` - Vectors and Matrices - Vecto va ma tran - Parent: `MATH_LINEAR_ALGEBRA_TOPICS`

## Explicit structured record with aliases

```json
{
  "vocabulary_type": "TOPIC",
  "code": "ML_LOGISTIC_REGRESSION",
  "parent_code": "ML_CLASSIFICATION_METHODS",
  "labels": {"en": "Logistic Regression", "vi": "Hoi quy logistic"},
  "status": "ACTIVE",
  "aliases": ["logit"]
}
```
