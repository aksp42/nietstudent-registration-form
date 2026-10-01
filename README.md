# Student Registration Form with GitHub Actions and Jenkins

A student registration web page whose code is tested automatically every time it changes, first by **GitHub Actions** and then by a **Jenkins** pipeline.

## Objective

The objective of this practical is to:

1. Create a professional, responsive **Student Registration Portal** using HTML5, CSS3 and JavaScript.
2. Write an automated test (`test.py`) that checks the page contains every required element.
3. Use **GitHub Actions** to run that test automatically on every push and pull request.
4. Use a **Jenkins Pipeline** (Checkout, Build, Test) to run the same test.
5. Demonstrate that a broken page makes both tools report a **failure**, and a fixed page makes them **pass** again.

This is the basic idea of **Continuous Integration (CI)**: every change is checked automatically so mistakes are found early.

## Technologies

| Technology | Used for |
|---|---|
| HTML5 | Page structure and form validation attributes |
| CSS3 | Responsive, modern design |
| JavaScript | Friendly validation messages |
| Python 3 | The automated test (`test.py`, standard library only) |
| Git | Version control |
| GitHub | Hosting the repository |
| GitHub Actions | Cloud CI that runs the test on push and pull request |
| Jenkins | Self-hosted CI server that runs the pipeline |

## Project Structure

```text
student-registration/
│
├── index.html                  The registration page (open this in a browser)
├── style.css                   All styling and responsive layout
├── script.js                   Client-side validation and the success message
├── test.py                     Automated tests (Python standard library only)
├── Jenkinsfile                 Jenkins pipeline: Checkout -> Build -> Test
├── README.md                   This file
│
└── .github/
    └── workflows/
        └── test.yml            GitHub Actions workflow "Student Registration CI"
```

| File | What it does |
|---|---|
| `index.html` | The form with 18 items: name, email, phone, date of birth, gender, roll number, course, department, semester, address, city, state, PIN/ZIP, password, confirm password, terms checkbox, Register and Clear buttons. Every field has a meaningful `id` and a label linked with `for`. |
| `style.css` | Colours, layout, hover and focus effects. Works on desktop, tablet and mobile. |
| `script.js` | Shows a clear message under a field when it is empty or wrong, checks that both passwords match, and shows a success message when everything is valid. |
| `test.py` | Reads `index.html` and checks files, form fields, validation attributes, buttons and the CSS/JS links. Exits with code 1 if anything is wrong. |
| `Jenkinsfile` | Tells Jenkins which stages to run. |
| `.github/workflows/test.yml` | Tells GitHub Actions when and how to run the test. |

## Run Locally

### 1. Open the page

Double-click `index.html`, or right-click it and choose **Open with** your browser. No server or installation is needed.

Try submitting the empty form to see the validation messages, then fill it in correctly to see the success message.

### 2. Run the automated test

Open a terminal in the `student-registration` folder and run:

```bash
python test.py
```

On Linux or macOS you may need `python3 test.py` instead.

Expected output (shortened):

```text
✓ index.html exists
✓ style.css exists
✓ script.js exists
✓ HTML contains <html>
✓ HTML contains <form>
✓ Registration form exists
✓ Heading "Student Registration Portal" exists
...
✓ Register button exists
✓ Reset/Clear button exists
✓ HTML links to style.css
✓ HTML links to script.js

All tests passed successfully!
```

## GitHub Setup

1. Create a new **empty** repository on GitHub (do not add a README there).
2. In your terminal, inside the `student-registration` folder, run:

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin <repository-url>
git push -u origin main
```

Replace `<repository-url>` with your repository address, for example `https://github.com/your-username/student-registration.git`.

### How GitHub Actions runs the tests

* GitHub looks for workflow files inside `.github/workflows/`.
* `test.yml` says: run on every **push** and every **pull request**.
* GitHub starts a fresh Ubuntu machine, checks out your code, installs Python and runs `python test.py`.
* If `test.py` exits with code 0, the run shows a **green tick**. If it exits with code 1, the run shows a **red cross**.

To see the result, open your repository on GitHub and click the **Actions** tab. Click the latest run, then the **Run automated tests** job, then the **Run tests** step to read the output.

## Jenkins Setup

**Before you start:** Jenkins needs Git and Python 3 installed on the machine that runs the job, and the *Git* and *Pipeline* plugins (both are included in the suggested plugins). Your code must already be pushed to GitHub.

1. Open Jenkins in your browser (usually `http://localhost:8080`).
2. Click **New Item**, enter a name such as `student-registration`, choose **Pipeline** and click **OK**.
3. Scroll to the **Pipeline** section and set **Definition** to **Pipeline script from SCM**.
4. Set **SCM** to **Git**.
5. In **Repository URL**, enter your GitHub repository URL. For a private repository, add credentials as well.
6. Set **Branch Specifier** to `*/main`.
7. Set **Script Path** to `Jenkinsfile`.
8. Click **Save**.
9. Click **Build Now**.
10. Under **Build History**, click the build number (for example `#1`), then click **Console Output**.
11. Verify that the output contains the lines below and ends with `Finished: SUCCESS`.

```text
Checking out source code from SCM...
Building Student Registration Project...
Found: index.html
Found: style.css
Found: script.js
Found: test.py
Running automated tests...
✓ index.html exists
...
All tests passed successfully!
Tests completed successfully.
SUCCESS: The Student Registration pipeline passed.
Pipeline finished.
Finished: SUCCESS
```

### Common Jenkins problems

| Problem | Fix |
|---|---|
| `python3: not found` | Install Python 3 on the Jenkins machine, or change `PYTHON_CMD` in the `Jenkinsfile` to `'python'`. |
| Jenkins runs on Windows | Replace each `sh` step in the `Jenkinsfile` with `bat`, and change the Build loop to `if exist index.html (echo Found) else (exit 1)` style commands. |
| Jenkins does not start by itself after a push | Click **Build Now** again, or enable *GitHub hook trigger* or *Poll SCM* in the job settings. |
| Repository not found | Check the URL, and add credentials for a private repository. |

## Failure Demonstration

This shows that automated testing catches mistakes. Do it in this order.

1. **Break the page.** Open `index.html` and make the email field disappear. The quickest way is to change this one word:

   ```html
   <input type="email" id="email" ...
   ```
   to
   ```html
   <input type="email" id="emailBroken" ...
   ```

   (You can also delete the whole email `<div class="field">` block.)

2. **Check locally (optional).** Run `python test.py`. You will see:

   ```text
   ✗ FAILED: Email field exists - no element with id="email" was found in index.html
   1 test(s) failed:
   ```

3. **Commit and push the broken version:**

   ```bash
   git add index.html
   git commit -m "Break email field to demonstrate failing tests"
   git push
   ```

4. **GitHub Actions fails.** Open the **Actions** tab. The newest run shows a red cross. Open it and read the failing **Run tests** step.

5. **Jenkins fails.** Click **Build Now** in Jenkins (or wait for your trigger). Open **Console Output**. The Test stage fails and the build ends with `Finished: FAILURE`. The `post { failure { ... } }` message is printed.

6. **Fix the page.** Restore the email field (`id="email"`).

7. **Commit and push the fix:**

   ```bash
   git add index.html
   git commit -m "Restore email field"
   git push
   ```

8. **Both pass again.** GitHub Actions shows a green tick, and a new Jenkins build ends with `Finished: SUCCESS`.

## Notes

* The form does not send data anywhere. A valid submission only shows a success message in the browser, because this practical focuses on testing and CI.
* `test.py` uses only Python's standard library, so there is nothing to install.
