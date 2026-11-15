"""Browser smoke tests for both deployed Streamlit cockpits.
Only navigation and rendering: never sends portfolio data or invokes paid AI.
"""
import os
import sys
import time
from playwright.sync_api import sync_playwright

TARGETS={
    "PMS Bersoch":"https://pms-max.streamlit.app/",
    "DEMO PMS Max":"https://demo-pms-max-mxqteogjttzuufoah5nwnj.streamlit.app/",
}

def diagnose(page, name):
    """Emit actionable UI state; never include portfolio values or full page text."""
    headings = page.locator("h1,h2,h3").all_text_contents()[:12]
    title = page.title()
    url = page.url
    likely_gateway = any(fragment in (title+" "+url).lower()
                         for fragment in ("sleep", "login", "auth", "sign in", "suspended"))
    print(f"{name}: page title={title!r}, url={url}, headings={headings}, gateway={likely_gateway}",flush=True)
    return likely_gateway


def inspect(page,name,url):
    page.goto(url,wait_until="domcontentloaded",timeout=60000)
    main_header=page.get_by_role("heading",name="Resumen",exact=True)
    # The app is often asleep at the Streamlit Cloud gateway. Try waking it.
    for attempt in range(3):
        try:
            main_header.first.wait_for(timeout=10000)
            break
        except Exception:
            diagnose(page,name)
            wake=page.get_by_text("Yes, get this app back up!",exact=False)
            if wake.count():
                wake.first.click(timeout=10000)
                page.wait_for_timeout(12000)
            elif attempt<2:
                page.reload(wait_until="domcontentloaded",timeout=60000)
    else:
        diagnose(page,name)
        raise RuntimeError("Production UI unavailable or gateway sleeping: Resumen heading never appeared")
    page.get_by_text("Patrimonio total",exact=False).first.wait_for(timeout=20000)
    print(name+": Resumen and portfolio widget visible",flush=True)
    for label,expected in [("Comparar Activos","Comparar"),("Simular Compra/Venta","Simulador")]:
        radio=page.get_by_text(label,exact=True)
        if not radio.count():
            diagnose(page,name)
            raise RuntimeError("Navigation control missing: "+label)
        radio.first.click(timeout=12000)
        page.get_by_role("heading",name=expected,exact=True).first.wait_for(timeout=20000)
        print(name+": "+label+" navigation OK",flush=True)
    button=page.get_by_role("button",name="Asesor IA")
    if button.count():
        button.first.click(timeout=15000)
        page.get_by_role("heading",name="Asesor IA",exact=True).first.wait_for(timeout=20000)
        print(name+": Asesor IA navigation OK",flush=True)
    page.screenshot(path="smoke_"+("demo" if "DEMO" in name else "bersoch")+".png",full_page=True)

def main():
    failures=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,args=["--no-sandbox"])
        for name,url in TARGETS.items():
            page=browser.new_page(viewport={"width":1600,"height":960},locale="es-AR")
            try:inspect(page,name,url)
            except Exception as e:
                failures.append(f"{name}: {type(e).__name__}: {e}")
                print(failures[-1],flush=True)
                page.screenshot(path="smoke_error_"+("demo" if "DEMO" in name else "bersoch")+".png",full_page=True)
            finally:page.close()
        browser.close()
    if failures:
        print("Browser navigation failures:",*failures,sep="\n")
        sys.exit(1)
    print("Both cockpits passed public browser navigation smoke checks.")

if __name__=="__main__": main()
