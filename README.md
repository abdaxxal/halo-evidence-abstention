# Halo Evidence Abstention

Can a model tell when its answer is no longer supported after a decisive fact disappears?

This solo Halo post-training project proposes using async GRPO to train an adapter for `gpt-oss-20b`. Each pair asks the same question with and without the specific sentence needed to answer it. Assessing both versions helps distinguish grounding in the provided evidence from a plausible guess.

**Current status:** CPU-only verifier prototype and four public synthetic smoke-test cases. Prediction examples are handwritten, not model outputs. No Halo config, model training, benchmark results, or competition submission yet.

## Run the prototype

Requires Python 3.10+ and no third-party packages.

```bash
python -m unittest -v
python verifier.py examples/cases.json examples/predictions.json
```

The verifier uses predeclared exact-match aliases with conservative normalization. A confidence value predicts whether the candidate is both correct and supported by the supplied evidence. The Brier loss is computed even if a separate confidence threshold suppresses the answer, so abstention cannot remove difficult cases from the calibration score. The threshold in this demo is illustrative.

The examples deliberately include a wrong, high-confidence answer borrowed from a neighboring record. The verifier flags it as wrong. The evidence strings do not produce their own labels: answer aliases and answerability are defined in the dataset, kept out of model inputs, and checked when constructing pairs.

## Planned experiment

- Split by document family and template; keep each pair together. Use a development split to set decision thresholds.
- Compare the same starting model with thresholding, correctness-only GRPO, and calibration-aware GRPO using the same evaluation protocol and matched training budgets where applicable.
- Report wrong answers at matched coverage, false answers on unanswerable cases, and Brier loss on all valid candidates. Report invalid-output rates separately, including failures in the total case denominator. Include paired uncertainty intervals and raw answerable accuracy.
- Pin the Halo revision, model, data split, and seeds before reporting results.

The fixtures are a public demonstration, not a locked evaluation set. This repository contains no private project or workplace material.

References: [Halo GPT-OSS cookbook](https://whitecircle.com/halo/docs/cookbooks/halo-gpt-oss-cookbook), [Beyond Binary Rewards](https://arxiv.org/abs/2507.16806), and [CalibraRL](https://arxiv.org/abs/2610.35142).

License: Apache-2.0.
