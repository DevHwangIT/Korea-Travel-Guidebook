from pathlib import Path

for slug in ["wonjo-nude-cheese", "oto", "horangi", "food2900"]:
    p = Path("pages/foods/meals/kimbap") / f"{slug}.html"
    t = p.read_text(encoding="utf-8")
    needle = f'restaurants.{slug}.about'
    if needle not in t:
        t = t.replace(
            '<table class="content-table">',
            f'<p data-i18n="{needle}"></p>\n    <table class="content-table">',
        )
    t = t.replace(
        f"Images/foods/kimbap-{slug}.jpg",
        f"Images/foods/restaurants/kimbap/{slug}.jpg",
    )
    p.write_text(t, encoding="utf-8")
    print("ok", slug)
