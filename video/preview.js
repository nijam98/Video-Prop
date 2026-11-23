const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
p.on('console',m=>console.log('console:',m.text()));p.on('pageerror',e=>console.log('ERR',e.message));
await p.goto('file://'+__dirname+'/index.html');await p.evaluate(()=>document.fonts.ready);await p.waitForFunction(()=>[...document.images].every(i=>i.complete&&i.naturalWidth>0));
const times=(process.argv[2]||'1,3,4.9,5.5,7.2,9.4,11.5,12.7,14.2,16,18.2,19.8').split(',').map(Number);
for(const t of times){await p.evaluate(t=>render(t),t);await p.screenshot({path:`${process.env.OUT}/f_${String(t).padStart(5,'0')}.png`});}
await b.close();})();
