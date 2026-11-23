"""Capture the real app and a silent walkthrough; start/stop an isolated local server."""
import os, sys, time, subprocess, urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'screenshots';OUT.mkdir(exist_ok=True)

def main():
    env=os.environ.copy();env['FORGE_LOG_DIR']=str(ROOT/'logs')
    proc=subprocess.Popen([sys.executable,'-m','streamlit','run','app.py','--server.port','8512','--server.address','127.0.0.1'],cwd=ROOT,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        for _ in range(80):
            try: opener.open('http://127.0.0.1:8512/_stcore/health',timeout=1);break
            except Exception: time.sleep(.25)
        else: raise RuntimeError('Streamlit failed to become healthy')
        with sync_playwright() as p:
            launch={'headless':True,'args':['--no-sandbox','--disable-dev-shm-usage']}
            if os.getenv('FORGE_CHROMIUM'): launch['executable_path']=os.environ['FORGE_CHROMIUM']
            browser=p.chromium.launch(**launch)
            # Record the actual rendered app; no generated/mock interface frames.
            ctx=browser.new_context(viewport={'width':1440,'height':1100},device_scale_factor=1,record_video_dir=str(ROOT/'sample_outputs'/'video'),record_video_size={'width':1440,'height':1100})
            page=ctx.new_page();page.goto('http://127.0.0.1:8512',wait_until='networkidle')
            page.get_by_role('button',name='Research Opportunity',exact=True).wait_for()
            def snap(name):
                page.wait_for_timeout(800)
                page.screenshot(path=str(OUT/name),full_page=True)
                page.wait_for_timeout(4000)
            page.get_by_text('Define the strategic problem',exact=True).scroll_into_view_if_needed()
            snap('01_challenge.png')
            page.get_by_role('button',name='Research Opportunity',exact=True).click()
            page.get_by_text('Research ready.',exact=False).wait_for()
            page.get_by_role('tab',name='2 · Evidence',exact=True).click()
            page.get_by_text('E1 · NASA describes simulated engine degradation data.',exact=True).scroll_into_view_if_needed()
            snap('02_evidence.png')
            page.get_by_role('checkbox',name='Include finding',exact=True).nth(3).focus()
            page.keyboard.press('Space')
            page.get_by_role('button',name='Approve Evidence & Continue',exact=True).click()
            page.get_by_role('button',name='Generate Technology Opportunities',exact=True).click()
            page.get_by_role('tab',name='3 · Opportunities',exact=True).click()
            page.get_by_text('Human gate 2 · Make the strategy decision',exact=True).wait_for()
            page.get_by_text('O1 · Engine-health forecasting benchmark',exact=True).click()
            page.get_by_text('O1 · Engine-health forecasting benchmark',exact=True).scroll_into_view_if_needed()
            snap('03_opportunities.png')
            page.get_by_label('Comments and priorities',exact=True).fill('Prioritize mechanic workload, low integration cost and a reversible pilot.')
            page.get_by_role('button',name='Approve Selection & Build Roadmap',exact=True).click()
            page.get_by_role('tab',name='4 · Roadmap',exact=True).click()
            page.get_by_role('button',name='Run Independent AI Strategy Review',exact=True).wait_for()
            page.get_by_text('Initial implementation roadmap',exact=True).scroll_into_view_if_needed()
            snap('04_roadmap.png')
            page.get_by_role('button',name='Run Independent AI Strategy Review',exact=True).click()
            page.get_by_role('tab',name='5 · Critic',exact=True).click()
            page.get_by_text('Strongest counterargument',exact=True).wait_for()
            page.get_by_text('Strongest counterargument',exact=True).scroll_into_view_if_needed()
            snap('05_critic.png')
            page.get_by_role('tab',name='6 · Final brief',exact=True).click()
            page.get_by_role('button',name='Download strategy brief (.md)',exact=True).wait_for()
            snap('06_final.png')
            with page.expect_download() as download:
                page.get_by_role('button',name='Download strategy brief (.md)',exact=True).click()
            download.value.save_as(str(ROOT/'sample_outputs'/'browser_downloaded_brief.md'))
            with page.expect_download() as download:
                page.get_by_role('button',name='Download full audit log (.json)',exact=True).click()
            download.value.save_as(str(ROOT/'sample_outputs'/'browser_session.json'))
            # Capture mobile layout without another app run.
            page.set_viewport_size({'width':390,'height':844})
            page.get_by_role('tab',name='1 · Challenge',exact=True).click()
            page.screenshot(path=str(OUT/'07_mobile.png'),full_page=True)
            assert not page.get_by_test_id('stException').count()
            video=page.video
            ctx.close()
            video.save_as(str(ROOT/'sample_outputs'/'FORGE_silent_demo.webm'))
            browser.close()
        print('Browser workflow, screenshots, downloads and mobile layout completed.')
    finally:
        proc.terminate();proc.wait(timeout=15)

if __name__=='__main__':main()
