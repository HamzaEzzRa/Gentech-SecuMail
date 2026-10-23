# SecuMail 2.0

GenTech 2026 email security project.

| Path          | Role                                                                    |
| ------------- | ----------------------------------------------------------------------- |
| `setup.ipynb` | Colab install: copies the project to the student's Drive                |
| `main.ipynb`  | student notebook, one section per session                               |
| `homework/`   | the only files students edit                                            |
| `src/`        | provided code: helpers, scoring engine, measures, verification, ML      |
| `workshop/`   | instructor slide decks (reveal.js), one per module                      |
| `data/`       | training emails, unlabelled test emails, brand domains |
| `tools/`      | teacher tools: corpus generator and grading                             |

## Student files

| File                         | Session | To do                                                   |
| ---------------------------- | ------- | ------------------------------------------------------- |
| `homework/phishing_rules.py` | 2       | fix `domaine_est_officiel`, write 4 rules               |
| `homework/spam_rules.py`     | 3       | complete 2 lists, write 3 functions                     |
| `homework/bayes.py`          | 4       | write 3 functions                                       |
| `homework/thresholds.py`     | 5       | tune `SEUIL_` (and the `POINTS_` of the two rule files) |

## Provided code

| File                    | Role                                                              |
| ----------------------- | ----------------------------------------------------------------- |
| `src/email.py`          | helpers: domains, links, brands, words                            |
| `src/scoring_engine.py` | provided rules, assembly of modules 1 and 2, decision, report     |
| `src/evaluation.py`     | confusion matrix, cost, prudent and permissive policies           |
| `src/pipeline.py`       | loading, validation split, threshold sweep, `predictions.csv`     |
| `src/verification.py`   | checks every student function: `OK`, `...` or `X`                 |
| `src/ml.py`             | module 3 training and prediction around `homework/bayes.py`       |

## Slides

Each `workshop/` notebook is one atelier deck with reveal.js slide metadata. Its demos
run live, so the build executes every deck before converting it. Its illustrations live
in `images/` next to the deck and are embedded in the HTML, so one file is enough to present.

```sh
uv run python tools/build_slides.py   # writes build/slides/seance<N>-<module>-<deck>.slides.html
```

## Teacher tools

```sh
# Regenerate the corpus (train, test and the hidden test key)
python tools/generate_corpus.py --ham 400 --spam 300 --phishing 300 \
    --test-share 0.3 -o data/emails_train.csv

# Score the teams' predictions.csv files on the hidden test set
python tools/grade.py submissions/*.csv
```

`data/emails_test_labels.csv` is the answer key. It is git-ignored and hidden from students.
