import { chromium } from 'playwright';
const base=process.argv[2], out=process.argv[3]||'screenshots';
const b=await chromium.launch({executablePath:'/usr/bin/google-chrome',args:['--no-sandbox']});
for (const [name,vp,mob] of [['mobile',{width:390,height:844},true],['desktop',{width:1366,height:900},false]]){
  const ctx=await b.newContext({viewport:vp,isMobile:mob,hasTouch:mob,deviceScaleFactor:mob?2:1});
  for (const p of ['areas/hamptons','areas/east-hampton','areas/westhampton','','areas/long-island-ny']){
    const pg=await ctx.newPage(); const errs=[];
    pg.on('pageerror',e=>errs.push(e.message)); pg.on('console',m=>{if(m.type()==='error')errs.push(m.text())});
    const r=await pg.goto(`${base}/${p}${p?'/':''}`,{waitUntil:'networkidle'});
    await pg.evaluate(async()=>{for(let y=0;y<document.body.scrollHeight;y+=600){window.scrollTo(0,y);await new Promise(r=>setTimeout(r,60));}window.scrollTo(0,0);});
    await pg.evaluate(()=>document.querySelectorAll('.reveal,.reveal-stagger,.reveal-stagger>*').forEach(e=>e.classList.add('revealed','is-visible','visible')));
    const ov=await pg.evaluate(()=>document.documentElement.scrollWidth-window.innerWidth);
    const broken=await pg.evaluate(()=>[...document.images].filter(i=>i.complete&&i.naturalWidth===0).map(i=>i.src));
    console.log(name,p||'home',r.status(),'overflowX',ov,'errors',errs.length,errs.slice(0,3),'brokenImgs',broken);
    const slug=(p.split('/').pop()||'home');
    if(['east-hampton','hamptons','westhampton'].includes(slug)||(slug==='home'&&!mob)) await pg.screenshot({path:`${out}/${slug}-${name}.png`,fullPage:true});
    await pg.close();
  }
  await ctx.close();
}
await b.close();
