#!/usr/bin/env python3
"""
test.py - automated checks for the Student Registration Portal.

Uses only Python's built-in modules, so nothing needs to be installed.
Run it with:   python test.py     (or python3 test.py)

Exit code 0 = every check passed.
Exit code 1 = at least one check failed (GitHub Actions and Jenkins
              treat this as a failed build).
"""

import sys
from html.parser import HTMLParser
from pathlib import Path

# Make the tick and cross symbols work on Windows consoles too.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

PROJECT_DIR = Path(__file__).resolve().parent
HTML_FILE = PROJECT_DIR / "index.html"
CSS_FILE = PROJECT_DIR / "style.css"
JS_FILE = PROJECT_DIR / "script.js"

PAGE_TITLE = "Student Registration Portal"


# ----------------------------------------------------------------------
# Step 1: a small HTML reader that remembers every tag it sees
# ----------------------------------------------------------------------
class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []            # every (tag name, attributes) pair
        self.by_id = {}           # id -> (tag name, attributes)
        self.label_targets = set()  # ids that some <label for="..."> points to
        self.options = {}         # select id -> list of option values
        self.text = {}            # tag name -> list of text found inside it
        self._open_text = None    # (tag name, collected pieces)
        self._current_select = None

    def handle_starttag(self, tag, attrs):
        attrs = {name: (value if value is not None else "") for name, value in attrs}
        self.tags.append((tag, attrs))

        if "id" in attrs:
            self.by_id[attrs["id"]] = (tag, attrs)
        if tag == "label" and "for" in attrs:
            self.label_targets.add(attrs["for"])
        if tag == "select":
            self._current_select = attrs.get("id")
            self.options[self._current_select] = []
        if tag == "option" and self._current_select is not None:
            self.options[self._current_select].append(attrs.get("value", ""))
        if tag in ("h1", "title", "button"):
            self._open_text = (tag, [])

    def handle_data(self, data):
        if self._open_text is not None:
            self._open_text[1].append(data)

    def handle_endtag(self, tag):
        if tag == "select":
            self._current_select = None
        if self._open_text is not None and self._open_text[0] == tag:
            joined = " ".join("".join(self._open_text[1]).split())
            self.text.setdefault(tag, []).append(joined)
            self._open_text = None

    def has_tag(self, tag_name):
        return any(tag == tag_name for tag, _ in self.tags)


# ----------------------------------------------------------------------
# Step 2: a tiny test reporter
# ----------------------------------------------------------------------
failures = []


def check(description, passed, problem=""):
    """Print a tick or a cross, and remember failures."""
    if passed:
        print(f"\u2713 {description}")
    else:
        message = f"{description} - {problem}" if problem else description
        print(f"\u2717 FAILED: {message}")
        failures.append(message)


def finish():
    print()
    if failures:
        print(f"{len(failures)} test(s) failed:")
        for item in failures:
            print(f"  - {item}")
        sys.exit(1)
    print("All tests passed successfully!")
    sys.exit(0)


# ----------------------------------------------------------------------
# Step 3: what the form must contain
# ----------------------------------------------------------------------
# (id, display name, tag, input type or None, validation attributes needed)
FIELDS = [
    ("fullName",        "Full Name",        "input",    "text",     ["required", "minlength", "maxlength", "pattern"]),
    ("email",           "Email",            "input",    "email",    ["required", "maxlength"]),
    ("phone",           "Phone",            "input",    "tel",      ["required", "minlength", "maxlength", "pattern"]),
    ("dob",             "Date of Birth",    "input",    "date",     ["required"]),
    ("rollNumber",      "Roll Number",      "input",    "text",     ["required", "minlength", "maxlength", "pattern"]),
    ("course",          "Course",           "select",   None,       ["required"]),
    ("department",      "Department",       "select",   None,       ["required"]),
    ("semester",        "Year/Semester",    "select",   None,       ["required"]),
    ("address",         "Address",          "textarea", None,       ["required", "minlength", "maxlength"]),
    ("city",            "City",             "input",    "text",     ["required", "minlength", "maxlength", "pattern"]),
    ("state",           "State",            "input",    "text",     ["required", "minlength", "maxlength", "pattern"]),
    ("pincode",         "PIN/ZIP Code",     "input",    "text",     ["required", "minlength", "maxlength", "pattern"]),
    ("password",        "Password",         "input",    "password", ["required", "minlength", "maxlength", "pattern"]),
    ("confirmPassword", "Confirm Password", "input",    "password", ["required", "minlength", "maxlength"]),
]

REQUIRED_COURSES = ["BCA", "B.Tech", "MCA", "MBA"]
GENDER_OPTIONS = [("genderMale", "Male"), ("genderFemale", "Female"), ("genderOther", "Other")]


def check_field(page, field_id, name, tag, input_type, needed):
    """Check that a field exists, has a label, and has validation attributes."""
    found = page.by_id.get(field_id)
    problems = []

    if found is None:
        problems.append(f'no element with id="{field_id}" was found in index.html')
    else:
        found_tag, attrs = found
        if found_tag != tag:
            problems.append(f'id="{field_id}" should be a <{tag}> but is a <{found_tag}>')
        if input_type and attrs.get("type") != input_type:
            problems.append(f'id="{field_id}" should have type="{input_type}"')
        if field_id not in page.label_targets:
            problems.append(f'no <label for="{field_id}"> is linked to this field')

    check(f"{name} field exists", not problems, "; ".join(problems))

    # Only check validation attributes when the field itself was found.
    if found is not None:
        missing = [attr for attr in needed if attr not in found[1]]
        check(
            f"{name} field has validation ({', '.join(needed)})",
            not missing,
            f'id="{field_id}" is missing: {", ".join(missing)}',
        )


# ----------------------------------------------------------------------
# Step 4: run all the checks
# ----------------------------------------------------------------------
def main():
    # --- Required files ---
    for path in (HTML_FILE, CSS_FILE, JS_FILE):
        check(f"{path.name} exists", path.is_file(), f"{path.name} was not found next to test.py")

    if not HTML_FILE.is_file():
        print("\nCannot continue without index.html.")
        finish()

    page = PageParser()
    page.feed(HTML_FILE.read_text(encoding="utf-8"))

    # --- Basic page structure ---
    check("HTML contains <html>", page.has_tag("html"), "the <html> tag is missing")
    check("HTML contains <form>", page.has_tag("form"), "the <form> tag is missing")

    form = page.by_id.get("registrationForm")
    check(
        "Registration form exists",
        form is not None and form[0] == "form",
        'the form with id="registrationForm" is missing',
    )

    headings = [h.lower() for h in page.text.get("h1", [])]
    titles = [t.lower() for t in page.text.get("title", [])]
    check(
        f'Heading "{PAGE_TITLE}" exists',
        any(PAGE_TITLE.lower() in h for h in headings),
        f'no <h1> containing "{PAGE_TITLE}" was found',
    )
    check(
        f'Page <title> is "{PAGE_TITLE}"',
        any(PAGE_TITLE.lower() in t for t in titles),
        f'the <title> does not contain "{PAGE_TITLE}"',
    )

    # --- Text, email, phone, date, select, textarea and password fields ---
    for field in FIELDS:
        check_field(page, *field)

    # --- Course options ---
    course_options = page.options.get("course", [])
    missing_courses = [c for c in REQUIRED_COURSES if c not in course_options]
    check(
        "Course field offers BCA, B.Tech, MCA and MBA",
        not missing_courses,
        "missing course option(s): " + ", ".join(missing_courses),
    )

    # --- Gender (a group of radio buttons) ---
    gender_group = page.by_id.get("gender")
    check("Gender field exists", gender_group is not None, 'no element with id="gender" was found')

    for radio_id, label in GENDER_OPTIONS:
        radio = page.by_id.get(radio_id)
        ok = (
            radio is not None
            and radio[1].get("type") == "radio"
            and radio[1].get("name") == "gender"
            and "required" in radio[1]
            and radio_id in page.label_targets
        )
        check(
            f"Gender option {label} exists",
            ok,
            f'needs <input type="radio" name="gender" required id="{radio_id}"> and a linked label',
        )

    # --- Terms checkbox ---
    terms = page.by_id.get("terms")
    check(
        "Terms checkbox exists",
        terms is not None
        and terms[1].get("type") == "checkbox"
        and "required" in terms[1]
        and "terms" in page.label_targets,
        'needs a required <input type="checkbox" id="terms"> with a linked label',
    )

    # --- Buttons ---
    register = page.by_id.get("registerBtn")
    check(
        "Register button exists",
        register is not None and register[0] == "button" and register[1].get("type") == "submit",
        'needs <button type="submit" id="registerBtn">',
    )

    reset = page.by_id.get("resetBtn")
    check(
        "Reset/Clear button exists",
        reset is not None and reset[0] == "button" and reset[1].get("type") == "reset",
        'needs <button type="reset" id="resetBtn">',
    )

    # --- CSS and JavaScript references ---
    has_css = any(
        tag == "link" and attrs.get("rel") == "stylesheet" and attrs.get("href") == "style.css"
        for tag, attrs in page.tags
    )
    check("HTML links to style.css", has_css, '<link rel="stylesheet" href="style.css"> is missing')

    has_js = any(tag == "script" and attrs.get("src") == "script.js" for tag, attrs in page.tags)
    check("HTML links to script.js", has_js, '<script src="script.js"></script> is missing')

    finish()


if __name__ == "__main__":
    main()
