// Renders index.html frame-by-frame into silent.mp4 and writes sfx.json
const {chromium}=require('playwright');const {spawn}=require('child_process');const fs=require('fs');
(async()=>{
  const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
  p.on('pageerror',e=>{console.error('ERR',e.message);process.exit(1)});
  await p.goto('file://'+__dirname+'/index.html');await p.evaluate(()=>document.fonts.ready);await p.waitForFunction(()=>[...document.images].every(i=>i.complete&&i.naturalWidth>0));
  const {DUR,FPS,SFX}=await p.evaluate(()=>({DUR:window.DURATION,FPS:window.FPS,SFX:window.SFX}));
  fs.writeFileSync(__dirname+'/sfx.json',JSON.stringify(SFX,null,1));
  const ff=spawn('ffmpeg',['-y','-loglevel','error','-f','image2pipe','-framerate',String(FPS),'-i','-',
    '-c:v','libx264','-preset','slow','-crf','17','-pix_fmt','yuv420p',__dirname+'/silent.mp4'],{stdio:['pipe','inherit','inherit']});
  const N=Math.round(DUR*FPS);
  for(let i=0;i<N;i++){await p.evaluate(t=>render(t),i/FPS);
    const buf=await p.screenshot({type:'jpeg',quality:95});
    if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));
    if(i%60===0)console.log('frame',i,'/',N);}
  ff.stdin.end();await new Promise(r=>ff.on('close',r));await b.close();console.log('done');
})();
