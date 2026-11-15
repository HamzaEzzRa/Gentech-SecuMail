# SecuMail 2.0

GenTech 2026 email security project.

| Path            | Role                                                                  |
| --------------- | --------------------------------------------------------------------- |
| `session<N>/`   | session N: `main.ipynb` and the file students write that day         |
| `src/`          | provided code, by module                                              |
| `data/`         | training emails, unlabelled test emails, brand domains                |
| `slides/`       | teacher decks (reveal.js), one folder per session, not in workspaces  |
| `resources/`    | course booklet, shown before slides and code in every platform session |
| `tools/`        | teacher tools: corpus generator, session check, slides and grading    |

## Student files

| File                         | Written in | Used in | To do                                         |
| ---------------------------- | ---------- | ------- | --------------------------------------------- |
| `session2/phishing_rules.py` | 2          | 1 to 5  | fix `domaine_est_officiel`, write 4 rules     |
| `session3/spam_rules.py`     | 3          | 3 to 5  | complete 2 lists, write 3 functions           |
| `session4/bayes.py`          | 4          | 4, 5    | write 3 functions                             |
| `session5/thresholds.py`     | 5          | 3 to 5  | tune `SEUIL_`, and the `POINTS_` of both rule files |

`eclorithme.yaml` gives each session its files: `open` as tabs, `files` without a tab.
Nothing arrives before its session is live or finished.

## Provided code

| File                    | Role                                                       |
| ----------------------- | ---------------------------------------------------------- |
| `src/startup.py`        | first cell of every notebook: path, autoreload, data       |
| `src/email.py`          | helpers: domains, links, brands, words                     |
| `src/pipeline.py`       | loading, validation split, `predictions.csv`               |
| `src/evaluation.py`     | old gateway, confusion matrix, cost, policies              |
| `src/phishing.py`       | module 1: provided rules and assembly                      |
| `src/spam.py`           | module 2: provided rules and assembly                      |
| `src/ml.py`             | module 3: training and prediction around `session4/bayes.py` |
| `src/scoring_engine.py` | decision, full report, threshold curves                    |
| `src/checks/`           | one check per module: `OK`, `...` or `X`                   |

The platform rewrites `src/` in student workspaces when it changes.
Notebooks and student files are copied once.

## Slides and checks

Each deck's demos run live, and its `images/` are embedded in the HTML.
The build first runs every session notebook with only the files students have that day.

```sh
uv run python tools/build_slides.py     # writes build/slides/session<N>-<deck>.slides.html
uv run python tools/check_sessions.py   # the session notebooks only
```

Both use the files git tracks. Run `git add` on a new file first.

## Course booklet

`resources/cahier-secumail.pdf` is the compiled student booklet from
`OL_Gentech_A2026/build/main.pdf`. Replace this PDF and commit it when the booklet
changes. The platform packages the committed version and shows it as the first
tab in every session. It is served separately from student workspaces.

## Teacher tools

```sh
# Regenerate the corpus (train, test and the hidden test key)
python tools/generate_corpus.py --ham 400 --spam 300 --phishing 300 \
    --test-share 0.3 -o data/emails_train.csv

# Score the teams' predictions.csv files on the hidden test set
python tools/grade.py submissions/*.csv
```

`data/emails_test_labels.csv` is the answer key. It is git-ignored and hidden from students.
