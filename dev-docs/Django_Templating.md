# Django Templating

## What Is Django Templating?

Most Django REST Framework views return **JSON**. A separate frontend (like React or Next.js) receives that JSON and decides how to display it. Django templating flips that around: Django itself builds the HTML and sends a fully rendered page back to the browser.

A Django template is an HTML file with a special syntax layered on top. Django fills in the real data server-side, and the browser receives a finished HTML page. No separate client needed.

### Why is this useful?

- **Internal reports** -- a staff member or analyst can open a URL and see a readable table or chart without needing a full frontend app
- **Admin-facing tools** -- simple pages for internal use that do not justify building a React component
- **PDF generation** -- many libraries generate PDFs from HTML, so a template is a natural first step
- **HTML emails** -- Django uses the same templating system to build and send HTML emails

The key idea: if the goal is a human-readable page rather than data for a client to consume, a template view is often the right tool.

---

## Step 1: Configure Django to Find Templates

Django needs to know where to look for template files. This is a one-line change in `settings.py`.

Find the `TEMPLATES` list. It will have a `DIRS` key that defaults to an empty list:

```python
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        ...
    },
]
```

Change `DIRS` to point at the `templates/` directory you will create in the project root:

```python
"DIRS": [BASE_DIR / "templates"],
```

`BASE_DIR` is already defined near the top of `settings.py` and points to the root of your project. The `/` operator on a `Path` object joins path segments, so `BASE_DIR / "templates"` resolves to the absolute path of your `templates/` folder.

---

## Step 2: Add a URL Route

Template-based report views use a plain URL path, not the DRF router. Add the route manually in `urls.py`, alongside your other manual paths like `login` and `register`:

```python
from projectapi.views.report_views import orders_report

path("reports/orders", orders_report, name="orders_report"),
```

This maps a GET request to `http://localhost:8000/reports/orders` to a function called `orders_report` that you will define in the next step.

Note that this imports from a **separate module** (`report_views`), not from the existing ViewSets. That separation is intentional and is covered in Step 4.

---

## Step 3: Create the Templates Directory

Create a `templates/` directory at the **project root**, alongside `tests/`, the project config directory, and the main app directory:

```text
your-project/
├── project/            # Django config (settings.py, urls.py, wsgi.py)
├── projectapi/         # Main Django app (models, views, fixtures)
├── tests/              # Test files
└── templates/          # Create this directory
```

This location is what `BASE_DIR / "templates"` points to after the `settings.py` change in Step 1. Django will search this directory when a view asks it to render a template.

---

## Step 4: Create a Standalone View Function

Template report views should **not** be added to existing ViewSets. ViewSets are designed for the REST API and carry two things that work against a template view:

1. They expect to return JSON `Response` objects
2. They enforce token authentication by default, so a browser hitting the URL without an `Authorization` header gets a 401 error

Instead, create a separate file for report views. A good convention is `projectapi/views/report_views.py`. Then export it from `projectapi/views/__init__.py` like any other view module.

The view function itself follows a simple pattern:

```python
from django.shortcuts import render
from projectapi.models import YourModel

def orders_report(request):
    orders = YourModel.objects.select_related("related_model", "other_model").all()
    context = {"orders": orders}
    return render(request, "reports/orders.html", context)
```

Three things to understand here:

**`select_related`** tells Django to fetch related model data in a single JOIN query upfront. Without it, if your template accesses `order.customer.name` for every row, Django fires a separate database query per row. With `select_related`, it fetches everything at once.

**`context`** is a plain Python dictionary. The keys you define here become the variable names available in the template. `{"orders": orders}` means the template can reference `orders` directly.

**`render(request, "reports/orders.html", context)`** takes the request, a path to the template file (relative to the `templates/` directory), and the context dictionary. It returns a full HTML response.

---

## Step 5: Create the Template File

Inside your `templates/` directory, create a `reports/` subdirectory, then an HTML file inside it. The path should match the string you passed to `render()`:

```text
templates/
└── reports/
    └── orders.html     (or ratings.html, or whatever fits your report)
```

### Boilerplate HTML

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Orders Report</title>
</head>
<body>
    <h1>Orders Report</h1>
    <table border="1">
        <thead>
            <tr>
                <th>Order ID</th>
                <th>Customer</th>
                <th>Total</th>
                <th>Payment Type</th>
            </tr>
        </thead>
        <tbody>
            {% for order in orders %}
            <tr>
                <td>{{ order.id }}</td>
                <td>{{ order.customer.username }}</td>
                <td>{{ order.total }}</td>
                <td>{{ order.payment_type }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</body>
</html>
```

### Template Syntax

Django templates use two kinds of tags:

**`{{ variable }}`** -- outputs a value. You can dot-chain through related objects following ForeignKey relationships:

```html
{{ order.customer.username }}
```

This follows the ForeignKey from `order` to `customer` and outputs the `username` field.

**`{% tag %}`** -- runs logic. The most common tag for reports is the `for` loop:

```html
{% for order in orders %}
    ...
{% endfor %}
```

`orders` matches the key in the context dictionary passed from the view. Everything between `{% for %}` and `{% endfor %}` repeats once per object in the queryset.

### Important syntax rules

- `{{ }}` with **no spaces** between the outer and inner braces. `{ { variable } }` will not be recognized and will output as literal text.
- Every `{% for %}` must have a matching `{% endfor %}`. Forgetting it causes a template syntax error.
- VS Code's JavaScript linter will flag Django template tags inside `<script>` blocks as errors. These are false positives -- Django processes the tags server-side before the browser ever sees the file, so the browser only receives plain JavaScript.

### What the example above produces

When Django renders this template, it loops over every order in the queryset and outputs one `<tr>` per row. The final HTML the browser receives is a static table with no template tags visible:

```html
<tr>
    <td>1</td>
    <td>john_doe</td>
    <td>47.99</td>
    <td>Visa</td>
</tr>
<tr>
    <td>2</td>
    <td>jane_smith</td>
    <td>22.50</td>
    <td>Mastercard</td>
</tr>
```

---

## Step 6: Run the Server and View the Report

Start the Django development server and open the report URL directly in a browser:

```text
http://localhost:8000/reports/orders
```

Because this is a plain Django view rather than a DRF endpoint, no `Authorization` token header is required. The browser can hit the URL directly and receive the rendered HTML page.
