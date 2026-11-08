import re,io,sys
p='/workspace/kwt/index.html'
s=open(p,encoding='utf-8').read()
def rep(old,new,cnt=1):
    global s
    assert s.count(old)>=1, 'MISSING: '+old[:80]
    s=s.replace(old,new,cnt)

# 1. toast aria
rep('<div class="toast" id="toast"></div>','<div class="toast" id="toast" role="status" aria-live="polite"></div>')
# 2. pull button aria
rep('<button class="iconbtn" id="pullbtn" title="Pull from Sheets">','<button class="iconbtn" id="pullbtn" title="Pull from Sheets" aria-label="Pull from Google Sheets">')
# 3. chart aria
rep('<canvas id="p-chart" height="180">','<canvas id="p-chart" height="180" role="img" aria-label="Production and overtime chart for the selected month">')
# 4. load core.js before inline script
rep("<script>\n'use strict';","<script src=\"js/core.js\"></script>\n<script>\n'use strict';")
# 5. remove helper block, keep app-side bits
m=re.search(r"const STATUSES=.*?function monthKey\(ds\)\{return ds\.slice\(0,7\)\}\n",s,re.S)
assert m,'helper block not found'
s=s[:m.start()]+"""/* statuses, months, date/time, math, validation and merge helpers live in js/core.js */
const RKEY='kwt_records',LKEY='kwt_log',CKEY='kwt_cfg',AKEY='kwt_auth';
function jget(k,d){try{return JSON.parse(localStorage.getItem(k))||d}catch(e){return d}}
function jset(k,v){localStorage.setItem(k,JSON.stringify(v))}
let records=jget(RKEY,{}),editlog=jget(LKEY,[]),cfg=jget(CKEY,{scriptUrl:'',shifts:{},deadline:'20:00'});
function toast(m){const t=$('toast');t.textContent=m;t.style.display='block';clearTimeout(t._t);t._t=setTimeout(()=>t.style.display='none',2600)}
function showErr(id,m){const e=$(id);e.textContent=m;e.style.display=m?'block':'none'}
"""+s[m.end():]
# 6. remove old istTs (h23 fix now in core.js)
m=re.search(r"function istTs\(\)\{.*?IST'\}\n",s,re.S)
assert m,'istTs not found'; s=s[:m.start()]+s[m.end():]
# 7. remove old agg
m=re.search(r"function agg\(list\)\{.*?\n\}\n",s,re.S)
assert m,'agg not found'; s=s[:m.start()]+s[m.end():]
# 8. CSV: escape every field
rep("""const rows=list.map(r=>[r.date,r.day,r.status,r.shift,r.hours,r.ot,r.prod,r.target,r.prod&&r.target?((r.prod/r.target)*100).toFixed(1):'',(r.remarks||'').replace(/"/g,'""'),r.leaveType||'',r.holidayName||'',r.updated||''].map(v=>'"'+String(v==null?'':v)+'"').join(',')).join('\\n');""",
"""const rows=list.map(r=>[r.date,r.day,r.status,r.shift,r.hours,r.ot,r.prod,r.target,r.prod&&r.target?((r.prod/r.target)*100).toFixed(1):'',r.remarks||'',r.leaveType||'',r.holidayName||'',r.updated||''].map(escCsv).join(',')).join('\\n');""")
# 9. import: only imported keys go back to unsynced
rep("Object.values(records).forEach(r=>r.synced=false);jset(RKEY,records);renderAll();",
    "Object.keys(d.records).forEach(k=>{if(records[k])records[k].synced=false});jset(RKEY,records);renderAll();")
# 10. changepw no-op line removal
rep("  $('s-changepw').onclick=()=>$('s-pwwrap').style.toggleAttribute?0:0;\n","")
# 11. secret helpers after pending()
rep("function pending(){return Object.values(records).filter(r=>!r.synced)}",
"""function pending(){return Object.values(records).filter(r=>!r.synced)}
function getSecret(){return sessionStorage.getItem('kwt_secret')||localStorage.getItem('kwt_secret')||''}
function saveSecret(v){v=String(v||'');sessionStorage.setItem('kwt_secret',v);const rb=$('s-remember');if(rb&&rb.checked)localStorage.setItem('kwt_secret',v);else localStorage.removeItem('kwt_secret')}""")
# 12. api(): demo guard + secret from getSecret()
rep("async function api(action,extra){\n  if(!cfg.scriptUrl)throw new Error('not-configured');",
    "async function api(action,extra){\n  if(window.KWT_DEMO)throw new Error('Demo mode: sync is disabled');\n  if(!cfg.scriptUrl)throw new Error('not-configured');")
rep("body:JSON.stringify(Object.assign({secret:cfg.secret,action},extra||{}))",
    "body:JSON.stringify(Object.assign({secret:getSecret(),action},extra||{}))")
# 13. setBadge demo branch
rep("function setBadge(){\n  const n=pending().length,b=$('syncbadge');",
    "function setBadge(){\n  const n=pending().length,b=$('syncbadge');\n  if(window.KWT_DEMO){b.textContent='Demo data';b.className='badge';return}")
# 14. testconn saves secret properly
rep("$('s-testconn').onclick=async()=>{cfg.scriptUrl=$('s-scripturl').value.trim();cfg.secret=$('s-secret').value;jset(CKEY,cfg);",
    "$('s-testconn').onclick=async()=>{cfg.scriptUrl=$('s-scripturl').value.trim();jset(CKEY,cfg);saveSecret($('s-secret').value);")
# 15. renderSet secret from getSecret()
rep("$('s-scripturl').value=cfg.scriptUrl||'';$('s-secret').value=cfg.secret||'';$('s-deadline').value=cfg.deadline||'20:00';",
    "$('s-scripturl').value=cfg.scriptUrl||'';$('s-secret').value=getSecret();$('s-deadline').value=cfg.deadline||'20:00';")
# 16. reminder hint reflects live shift reminders
rep('<p class="hint">Fo reads this deadline and reminds you once a day by text if no entry exists for that date. Sundays, holidays and approved leaves are skipped automatically.</p>',
    '<p class="hint">Shift-end reminders are already live: Fo texts you at 3:30 PM (A shift), 12:00 AM (B shift) or 6:30 AM (C shift) per your A/C/B roster, from 10 Nov 2026 to 31 Mar 2027. This deadline field is not used by those reminders.</p>')
# 17. pull() uses tested mergePulled
rep("""    const j=await api('getAll');let n=0;
    (j.records||[]).forEach(sr=>{
      const k=sr.date;const lo=records[k];
      if(!lo||String(lo.updated||'')<String(sr.updated||'')){records[k]=Object.assign({},sr,{synced:true});n++}
      else records[k].synced=true;
    });""",
"""    const j=await api('getAll');
    const n=mergePulled(records,j.records||[]);""")
# 18. demo boot + optional ?view=
rep("  if(authed())enterApp();else bootAuth();",
"""  if(new URLSearchParams(location.search).has('demo')){
    window.KWT_DEMO=true;records=makeDemo();cfg.shifts={A:{h:8,t:200},B:{h:8,t:180},C:{h:8,t:180}};enterApp();
    const v=new URLSearchParams(location.search).get('view');
    if(v&&['cal','rep','prod','set'].indexOf(v)>=0)switchTab(v);
  }
  else if(authed())enterApp();else bootAuth();""")
# 19. hero card on Today page
rep('<section class="page on" id="page-today">\n    <div class="card">\n      <h2>Daily entry</h2>',
"""<section class="page on" id="page-today">
    <div class="card hero">
      <div class="herotop">
        <div>
          <p class="hello">Hi Kehar <span class="wave">&#128075;</span></p>
          <p class="herodate" id="hero-date"></p>
        </div>
        <div class="heroshift" id="hero-shift"></div>
      </div>
      <div class="herostats" id="hero-stats"></div>
    </div>
    <div class="card">
      <h2>Daily entry</h2>""")
# 20. renderHero + call sites
rep("/* ---------- nav ---------- */",
"""/* ---------- today hero ---------- */
function renderHero(){
  const t=istToday();
  $('hero-date').textContent=dayName(t)+', '+Number(t.slice(8))+' '+MONTHS[Number(t.slice(5,7))-1]+' '+t.slice(0,4);
  const r=records[t],hs=$('hero-shift');
  if(r&&r.status){hs.innerHTML='<span class="pill st-'+r.status.replace(' ','')+'">'+esc(r.status)+'</span>'+(r.shift?' <span class="pill shift">Shift '+esc(r.shift)+'</span>':'')}
  else{hs.innerHTML='<span class="pill pend">Not saved yet</span>'}
  const mk=monthKey(t),a=agg(Object.values(records).filter(x=>monthKey(x.date)===mk));
  $('hero-stats').innerHTML=
   '<div class="stat"><div class="v">'+a.present+'</div><div class="l">Present days</div></div>'+
   '<div class="stat"><div class="v">'+a.ot.toFixed(1)+'</div><div class="l">OT hours</div></div>'+
   '<div class="stat"><div class="v">'+fmtPct(a.achv)+'</div><div class="l">Achievement</div></div>';
}
/* ---------- nav ---------- */""")
rep("  buildChips();loadForm(istToday());setBadge();renderSet();","  buildChips();loadForm(istToday());setBadge();renderSet();renderHero();")
rep("function renderAll(){setBadge();","function renderAll(){setBadge();renderHero();")
rep("  saveRec(r);loadForm(date);setBadge();","  saveRec(r);loadForm(date);setBadge();renderHero();")
# 21. calendar day cells: aria-label + keyboard operable
rep("""    h+='<div class="d'+(ds===today?' today':'')+'" data-d="'+ds+'">'+d+(r?'<span class="dot" style="background:'+SCOLORS[r.status]+'"></span>':'')+'</div>';""",
"""    const lbl=d+' '+MONTHS[calM]+' '+calY+(r?', '+r.status:'');
    h+='<div class="d'+(ds===today?' today':'')+'" data-d="'+ds+'" role="button" tabindex="0" aria-label="'+esc(lbl)+'">'+d+(r?'<span class="dot" style="background:'+SCOLORS[r.status]+'"></span>':'')+'</div>';""")
rep("  $('cal-grid').onclick=e=>{const el=e.target.closest('.d');if(!el||!el.dataset.d)return;switchTab('today');loadForm(el.dataset.d)};",
"""  $('cal-grid').onclick=e=>{const el=e.target.closest('.d');if(!el||!el.dataset.d)return;switchTab('today');loadForm(el.dataset.d)};
  $('cal-grid').onkeydown=e=>{if(e.key!=='Enter'&&e.key!==' ')return;const el=e.target.closest('.d');if(!el||!el.dataset.d)return;e.preventDefault();switchTab('today');loadForm(el.dataset.d)};""")
# 22. yearly table + prod table scroll wrappers
rep("$('r-yearbody').innerHTML='<table>","$('r-yearbody').innerHTML='<div class=\"tblwrap\"><table>")
rep("a.achv)+'</b></td></tr></table>';\n}\n/* ---------- production ---------- */",
    "a.achv)+'</b></td></tr></table></div>';\n}\n/* ---------- production ---------- */")
rep("h+='<table><tr><th>Date","h+='<div class=\"tblwrap\"><table><tr><th>Date")
rep("h+='</table>'}","h+='</table></div>'}")
open(p,'w',encoding='utf-8').write(s)
print('patch1 OK, size',len(s))
