# CodeSift

**An AI-assisted test generation system that investigates whether execution feedback helps improve automatically generated software tests.**

CodeSift explores a simple question: does an AI model generate better tests when it can execute its initial tests, inspect the results, and revise the test suite?

The project compares two approaches:

- **Baseline:** the model generates a test suite without receiving execution feedback.
- **Execution feedback:** the model generates an initial test suite, the tests are executed against the buggy implementation, and the execution results are sent back to the model so it can revise the suite.

The experiment uses a controlled benchmark of small Python functions with deliberately introduced bugs.

---

## Research question

**Does allowing an AI agent to execute generated tests and use the resulting feedback improve its ability to detect seeded software bugs compared with generating tests without execution feedback?**

The aim is to evaluate both bug-detection performance and the additional time required by the feedback process.

## Key findings

The experiment was conducted across **5 trials** and **18 benchmark cases**, giving **90 paired comparisons**.

| Metric | Baseline | Execution feedback |
|---|---:|---:|
| Seeded bugs detected | 90/90 | 90/90 |
| Tests generated | 664 | 664 |
| Genuine bug-detecting tests | 231 | 231 |
| False-positive tests | 1 | 1 |
| Total generation time | 500.91 sec | 911.66 sec |
| Average time per case | 5.57 sec | 10.13 sec |

### What the results suggest

- Both approaches detected all seeded bugs in the benchmark.
- Execution feedback did not increase the number of bugs detected or genuine bug-detecting tests.
- The feedback approach took approximately **82% more time** than the baseline.
- In **89 out of 90 comparisons**, the revised test suite was identical to the initial suite. The one difference was a test-name change, not a change to the test input or expected output.

The baseline already detected every seeded bug. This creates a ceiling effect, meaning this benchmark did not leave room for the feedback approach to achieve a higher bug-detection rate. The results therefore do not prove that execution feedback is ineffective in general. They show that it did not improve detection on this particular benchmark and model configuration.

## How the experiment works

Each benchmark case contains a function with a seeded bug and a corresponding fixed implementation.

1. The model receives the buggy function and a description of its intended behaviour.
2. It generates an initial test suite.
3. The baseline test suite is evaluated.
4. For the feedback approach, the initial tests are executed against the buggy implementation.
5. The execution results are sent to the model, which can revise its test suite.
6. The generated tests are evaluated locally against both the buggy and fixed implementations.

A test counts as a **genuine bug detection** when it fails on the buggy implementation but passes on the fixed implementation. A test that also fails on the fixed implementation is counted as a false positive.

The baseline and feedback approaches share the same initial generated suite for each paired comparison. This helps keep the comparison fair.

### Experimental configuration

| Setting | Value |
|---|---|
| Model | Gemini 3.5 Flash Lite |
| Benchmark | `benchmark_v3_1` |
| Number of benchmark cases | 18 |
| Number of trials | 5 |
| Maximum tests per suite | 8 |
| Trial design | `paired_shared_initial_suite_v1` |
| Test-generation prompt | `test_generation_v2` |
| Feedback prompt | `execution_feedback_v1` |
| Evaluator | `type_aware_float_tolerance_v1` |

## Benchmark cases

The benchmark contains 18 function-level cases:

| ID | Functionality being tested |
|---|---|
| CS001 | Discount calculation |
| CS002 | Adult age boundary |
| CS003 | Average of an empty input |
| CS004 | Stable unique elements |
| CS005 | Middle values |
| CS006 | Second-largest distinct value |
| CS007 | Tax threshold |
| CS008 | Free-shipping threshold |
| CS009 | Leap-year century rule |
| CS010 | Upper-bound clamping |
| CS011 | Counting occurrences, including the final element |
| CS012 | Merging sorted lists with equal elements |
| CS013 | Binary search final candidate |
| CS014 | Removing negative values without removing zero |
| CS015 | Word-frequency case sensitivity |
| CS016 | List rotation with a large shift |
| CS017 | Palindrome handling of spaces |
| CS018 | Missing number at the upper endpoint |

## Technology stack

- **Python 3.12+** for the experiment and test-generation workflow.
- **Google Gemini API** through the `google-genai` Python SDK.
- **python-dotenv** for loading the API key from a local environment file.
- **pytest** for running the project tests and validating behaviour.

## Project structure

The main folders and files are organised as follows. The tree below shows the key project areas and scripts used in the experiment.

```text
codesift/
│
├── README.md
├── .gitignore
├── .env.example
├── requirements.txt
│
├── src/
│   └── ...                 # Core CodeSift modules
│
├── scripts/
│   ├── run_experiment.py   # Runs an experiment trial
│   ├── generate_demo.py    # Generates a demonstration test suite
│   ├── execute_demo.py     # Executes the demonstration tests
│   ├── feedback_loop.py    # Demonstrates the execution-feedback loop
│   └── compare_suites.py   # Compares generated test suites
│
├── tests/
│   └── ...                 # Automated project and benchmark tests
│
└── reports/
    └── ...                 # Generated demonstration and trial outputs
```

The `reports/` folder is used for generated outputs when running the scripts. The full trial output files are not required to understand the headline findings reported above.

## Getting started

### 1. Clone the repository

Open PowerShell or a terminal and run:

```bash
git clone https://github.com/palakrajput16/codesift-ai
cd codesift
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

On macOS or Linux:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

The project uses `pytest`, `google-genai`, and `python-dotenv`.

### 4. Set up the Gemini API key

Create a file named `.env` in the project root and add:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

Replace the placeholder with your own Gemini API key.

**Important:** Do not commit your `.env` file or share your API key. The `.env` file should be excluded through `.gitignore`. If the repository includes `.env.example`, use it as a template and keep the real key only in `.env`.

### 5. Set the Python import path

In Windows PowerShell, run:

```powershell
$env:PYTHONPATH = "src"
```

If you open a new terminal, set this variable again before running the scripts.

### 6. Run the tests

```bash
pytest -v
```

### 7. Run a demonstration

Generate a demonstration test suite:

```bash
python scripts/generate_demo.py
```

The generated demonstration output is saved under `reports/`.

To execute the demonstration:

```bash
python scripts/execute_demo.py
```

### 8. Run an experiment trial

To run Trial 1:

```bash
python scripts/run_experiment.py --trial 1
```

To run another trial, change the trial number:

```bash
python scripts/run_experiment.py --trial 2
```

To resume an interrupted trial:

```bash
python scripts/run_experiment.py --trial 1 --resume
```

The experiment requires a working Gemini API key and an active internet connection. API availability, quotas, and rate limits may affect execution.

## What counts as a successful test?

CodeSift distinguishes between a test that catches the seeded bug and a test that simply fails.

- **Genuine detection:** the test fails on the buggy implementation and passes on the fixed implementation.
- **False positive:** the test also fails on the fixed implementation.
- **No detection:** the test passes on the buggy implementation.

This distinction matters because a test suite should identify real defects without incorrectly rejecting correct behaviour.

## Limitations

- The benchmark contains 18 small Python function-level cases. It does not represent every type of software defect or a large production codebase.
- The baseline detected all seeded bugs, so the experiment had a ceiling effect.
- Results are specific to the model, prompts, benchmark, and configuration used.
- Some API requests encountered errors and had to be retried. All 90 paired case-trial observations were eventually completed.
- Exact token usage and API cost were not available from the API responses used in this experiment. Generation time is reported instead of claiming an exact monetary cost.
- The CS017 palindrome case produced one false-positive test in Trial 4. Its expected result assumed punctuation and capitalization would be ignored, while the benchmark description only specified ignoring spaces. This is a specification ambiguity and is retained in the reported results.

## Future improvements

- Evaluate the feedback approach on more difficult cases where the baseline does not detect every seeded bug.
- Expand the benchmark to include more complex functions and different categories of bugs.
- Explore ways to make execution feedback lead to meaningful test-suite improvements.
- Track additional efficiency measures when reliable API usage data is available.

## Running the project safely

- Keep API keys in `.env`, never directly in source code.
- Do not commit virtual environments, cache folders, or secret files.
- Check API quotas and rate limits before running multiple trials.
- Use the same benchmark and configuration when comparing experimental runs.

## Author

**Palak Rajput**

Computer Science undergraduate interested in software testing, AI agents, and practical applications of machine learning.

---

*CodeSift is an experimental project. Its findings describe the tested benchmark and configuration, not a general claim that execution feedback can never improve AI-generated tests.*
