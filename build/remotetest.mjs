import { chromium, devices } from 'playwright';
const B=process.env.BASE||'https://trimoco-site.onrender.com';
const b=await chromium.launch({executablePath:'/usr/bin/google-chrome',args:['--no-sandbox']});
const errs=[]; const ctx=await b.newContext({viewport:{width:1366,height:900}}); const pg=await ctx.newPage(); pg.on('pageerror',e=>errs.push(e.message));
// block any real form send
let posted=null; await ctx.route('**/formsubmit.co/**',r=>{posted=r.request().postData();r.fulfill({status:200,contentType:'application/json',body:'{"success":"true"}'})});
await ctx.route('**/api.stonesystems.io/**',r=>{errs.push('stonesystems call '+r.request().url());r.abort()});
await pg.goto(B+'/'); const a=pg.locator('a.proj-link').first(); const href=await a.getAttribute('href'); await a.scrollIntoViewIfNeeded(); await pg.waitForTimeout(600); await a.click(); await pg.waitForURL('**'+href); console.log('home photo ->',new URL(pg.url()).pathname);
await pg.goto(B+'/projects/west-village-marble-kitchen-bathroom-renovation/');
await pg.locator('[data-lb-index="0"]').click(); await pg.waitForTimeout(300); const c1=await pg.locator('.lb-count').textContent();
await pg.keyboard.press('ArrowRight'); const c2=await pg.locator('.lb-count').textContent(); await pg.keyboard.press('Escape'); await pg.waitForTimeout(200);
console.log('lightbox',c1,'->',c2,'closed',!(await pg.locator('#lb').evaluate(d=>d.open)));
// quote form (mocked)
await pg.goto(B+'/areas/manhattan-ny/'); await pg.screenshot({path:'screenshots/render-manhattan-desktop.png'});
await pg.locator('#local-projects-heading').scrollIntoViewIfNeeded(); await pg.waitForTimeout(800); await pg.screenshot({path:'screenshots/render-manhattan-projects.png'});
await pg.locator('[data-open-quote-modal]').first().click(); await pg.waitForTimeout(500);
const dlg=pg.locator('dialog[open], [role=dialog]:visible').last();
const fill=async(sel,v)=>{const l=dlg.locator(sel).first(); if(await l.count()) await l.fill(v)};
await fill('input[name*=name i]','Test Person'); await fill('input[type=tel]','5165550123'); await fill('input[type=email]','test@example.com'); await fill('textarea','Mocked test - please ignore');
const cb=dlg.locator('input[type=checkbox]'); for(let k=0;k<await cb.count();k++) await cb.nth(k).check().catch(()=>{});
await dlg.locator('button[type=submit]').first().click().catch(e=>errs.push('submit '+e.message)); await pg.waitForTimeout(2000);
console.log('form posted (mocked):',posted?posted.slice(0,160):null);
// mobile swipe
const m=await b.newContext({...devices['iPhone 13'],hasTouch:true}); const mp=await m.newPage(); mp.on('pageerror',e=>errs.push(e.message));
await mp.goto(B+'/projects/soho-manhattan-bathroom-walk-in-shower/'); await mp.screenshot({path:'screenshots/render-project-mobile.png'});
await mp.locator('[data-lb-index="0"]').tap(); await mp.waitForTimeout(400); const st=await mp.locator('.lb-stage').boundingBox(); const y=st.y+st.height/2;
await mp.mouse.move(st.x+st.width*.8,y); await mp.mouse.down(); await mp.mouse.move(st.x+st.width*.2,y,{steps:5}); await mp.mouse.up(); await mp.waitForTimeout(300);
console.log('mobile swipe ->',await mp.locator('.lb-count').textContent());
await mp.goto(B+'/'); await mp.screenshot({path:'screenshots/render-home-mobile.png'});
console.log('errors',errs); await b.close();
