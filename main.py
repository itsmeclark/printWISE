"""PrintWise: PyScript logic. Every feature below is driven by a browser event."""
from html import escape
from pyscript import document, when

PRICES = {"bw": 1.0, "color": 3.0, "photo": 5.0}
TYPE_NAMES = {"bw": "B&W", "color": "Color", "photo": "Photo"}
STATUSES = ["Pending", "Printing", "Ready", "Picked up"]
orders = []


def peso(x):
    return f"₱{x:,.2f}"


def num(el_id, default=0.0):
    try:
        return max(float(document.querySelector(f"#{el_id}").value), 0.0)
    except ValueError:
        return default


def text(el_id, value):
    document.querySelector(f"#{el_id}").textContent = value


# ---------- Order form ----------
def order_total():
    kind = document.querySelector("#o-type").value
    pages, copies = int(num("o-pages")), int(num("o-copies"))
    return kind, pages, copies, pages * copies * PRICES[kind]


@when("input", ".order-input")
def update_quote(event=None):
    kind, pages, copies, total = order_total()
    text("o-summary", f"{pages} pages × {copies} copies × {peso(PRICES[kind])}")
    text("o-total", peso(total))


@when("submit", "#order-form")
def place_order(event):
    event.preventDefault()
    msg = document.querySelector("#o-msg")
    kind, pages, copies, total = order_total()
    name = document.querySelector("#o-name").value.strip()
    if not name or pages < 1 or copies < 1:
        msg.textContent = "Enter your name, at least 1 page, and at least 1 copy."
        msg.className = "msg err"
        return
    orders.append({
        "id": len(orders) + 1, "name": name,
        "course": document.querySelector("#o-course").value.strip(),
        "file": document.querySelector("#o-file").value.strip() or "(file at counter)",
        "kind": kind, "size": document.querySelector("#o-size").value,
        "pages": pages, "copies": copies, "total": total, "status": 0})
    msg.textContent = f"Order #{len(orders)} placed. Total {peso(total)}."
    msg.className = "msg ok"
    document.querySelector("#o-file").value = ""
    render_queue()


# ---------- Queue ----------
def render_queue():
    ul = document.querySelector("#queue")
    if not orders:
        ul.innerHTML = '<li class="empty">No orders yet. Place an order above and it will show up here.</li>'
    else:
        rows = []
        for o in reversed(orders):
            st = STATUSES[o["status"]]
            btn = "" if o["status"] == 3 else f'<button data-id="{o["id"]}" class="next">Mark as {STATUSES[o["status"] + 1].lower()}</button>'
            rows.append(
                f'<li class="s{o["status"]}"><div><b>#{o["id"]} {escape(o["name"])}</b> {escape(o["course"])}'
                f'<br><small>{escape(o["file"])} · {TYPE_NAMES[o["kind"]]} · {o["size"]} · '
                f'{o["pages"]} pg × {o["copies"]}</small></div>'
                f'<div class="r"><b>{peso(o["total"])}</b><span class="tag">{st}</span>{btn}</div></li>')
        ul.innerHTML = "".join(rows)
    text("q-count", str(len(orders)))
    text("q-pages", str(sum(o["pages"] * o["copies"] for o in orders)))
    text("q-sales", peso(sum(o["total"] for o in orders)))


@when("click", "#queue")
def advance_status(event):
    btn = event.target
    if btn.classList.contains("next"):
        o = orders[int(btn.dataset.id) - 1]
        o["status"] = min(o["status"] + 1, 3)
        render_queue()


@when("click", "#clear-queue")
def clear_queue(event):
    orders.clear()
    render_queue()


# ---------- Startup ----------
update_quote()
render_queue()