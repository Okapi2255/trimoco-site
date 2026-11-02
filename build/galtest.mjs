import { chromium, devices } from 'playwright';
const B='http://127.0.0.1:8765';
const b=await chromium.launch({executablePath:'/usr/bin/google-chrome',args:['--no-sandbox']});
const ctx=await b.newContext({viewport:{width:1366,height:900}}); const pg=await ctx.newPage();
const errs=[]; pg.on('pageerror',e=>errs.push(e.message));
await pg.goto(B+'/'); const a=pg.locator('a.proj-link').first(); const href=await a.getAttribute('href');
await a.scrollIntoViewIfNeeded(); await pg.waitForTimeout(800); await a.click(); await pg.waitForURL('**'+href);
console.log('home photo ->',pg.url());
await pg.goto(B+'/projects/kitchen-and-marble-bathroom-renovation/');
await pg.screenshot({path:'screenshots/project-page-desktop.png'});
await pg.locator('[data-lb-index="0"]').click(); await pg.waitForTimeout(400);
console.log('dialog open',await pg.locator('#lb').evaluate(d=>d.open), await pg.locator('.lb-count').textContent());
await pg.keyboard.press('ArrowRight'); console.log('after →',await pg.locator('.lb-count').textContent());
await pg.keyboard.press('ArrowLeft'); await pg.keyboard.press('ArrowLeft'); console.log('after ←←',await pg.locator('.lb-count').textContent());
await pg.waitForTimeout(500); await pg.screenshot({path:'screenshots/project-lightbox-desktop.png'});
await pg.keyboard.press('Escape'); await pg.waitForTimeout(200);
console.log('closed',!(await pg.locator('#lb').evaluate(d=>d.open)),'focus returned',await pg.evaluate(()=>document.activeElement.dataset.lbIndex));
// keyboard open
await pg.locator('[data-lb-index="2"]').focus(); await pg.keyboard.press('Enter'); await pg.waitForTimeout(200);
console.log('enter opens',await pg.locator('.lb-count').textContent()); await pg.keyboard.press('Escape');
// quote button
await pg.locator('[data-open-quote-modal]').first().click(); await pg.waitForTimeout(400);
console.log('quote modal visible',await pg.locator('dialog[open], [role=dialog]:visible').count());
// mobile swipe
const m=await b.newContext({...devices['iPhone 13'],hasTouch:true}); const mp=await m.newPage(); mp.on('pageerror',e=>errs.push(e.message));
await mp.goto(B+'/projects/kitchen-and-marble-bathroom-renovation/'); await mp.screenshot({path:'screenshots/project-page-mobile.png'});
await mp.locator('[data-lb-index="0"]').tap(); await mp.waitForTimeout(400);
const st=await mp.locator('.lb-stage').boundingBox(); const y=st.y+st.height/2;
await mp.mouse.move(st.x+st.width*0.8,y); await mp.mouse.down(); await mp.mouse.move(st.x+st.width*0.2,y,{steps:5}); await mp.mouse.up();
await mp.waitForTimeout(400); console.log('swipe ->',await mp.locator('.lb-count').textContent(),'still open',await mp.locator('#lb').evaluate(d=>d.open));
await mp.screenshot({path:'screenshots/project-lightbox-mobile.png'});
await mp.goto(B+'/projects/'); const n=await mp.locator('a.proj-link').count(); console.log('projects page links',n);
console.log('errors',errs); await b.close();
