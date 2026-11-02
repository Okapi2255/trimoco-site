import { chromium } from 'playwright';
const base='http://127.0.0.1:8765';
const pages=[['home','/'],['manhattan','/areas/manhattan-ny/'],['coop','/services/general-contractor/co-op-condo-renovation/']];
const b=await chromium.launch({executablePath:'/usr/bin/google-chrome',args:['--no-sandbox']});
const errs=[];
for (const [vp,opt] of [['mobile',{viewport:{width:390,height:844},deviceScaleFactor:2,isMobile:true,hasTouch:true}],['desktop',{viewport:{width:1440,height:900}}]]){
  const ctx=await b.newContext(opt);
  for (const [n,p] of pages){
    const pg=await ctx.newPage();
    pg.on('pageerror',e=>errs.push(`${n} ${vp}: ${e.message}`));
    pg.on('requestfailed',r=>errs.push(`${n} ${vp} FAIL ${r.url()}`));
    await pg.goto(base+p,{waitUntil:'networkidle'}).catch(e=>errs.push(String(e)));
    await pg.evaluate(async()=>{for(let y=0;y<document.body.scrollHeight;y+=600){window.scrollTo(0,y);await new Promise(r=>setTimeout(r,60));}window.scrollTo(0,0);});
    await pg.waitForTimeout(800);
    await pg.screenshot({path:`screenshots/${n}-${vp}.png`});
    await pg.screenshot({path:`screenshots/${n}-${vp}-full.png`,fullPage:true});
    await pg.close();
  }
  await ctx.close();
}
await b.close(); console.log(errs.join('\n')||'no errors');
