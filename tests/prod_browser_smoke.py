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

def inspect(page,name,url):
    page.goto(url,wait_until="domcontentloaded",timeout=60000)
    for attempt in range(3):
        page.wait_for_timeout(1800)
        wake=page.get_by_text("Yes, get this app back up!",exact=False)
        if wake.count():
            wake.first.click(timeout=12000)
            page.wait_for_timeout(15000)
            continue
        if page.get_by_role("heading",name="Resumen",exact=True).count():
            break
        page.wait_for_timeout(10000)
        if attempt==2:page.reload(wait_until="domcontentloaded",timeout=60000)
    page.get_by_role("heading",name="Resumen",exact=True).wait_for(timeout=60000)
    page.get_by_text("Patrimonio total",exact=False).first.wait_for(timeout=30000)
    print(name+": Resumen and NAV widget visible",flush=True)
    # Verify sidebar tools without triggering any trading or external AI calls.
    for label,expected in [("Comparar Activos","Comparar"),("Simular Compra/Venta","Simulador")]:
        radio=page.get_by_text(label,exact=True)
        radio.first.click(timeout=20000)
        page.wait_for_timeout(1800)
        assert expected.lower() in page.locator("h1").all_text_contents()[-1].lower(),(name,label,page.locator("h1").all_text_contents())
        print(name+": "+label+" navigation OK",flush=True)
    button=page.get_by_role("button",name="Asesor IA")
    if button.count():
        button.first.click(timeout=15000)
        page.get_by_role("heading",name="Asesor IA",exact=True).wait_for(timeout=25000)
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
