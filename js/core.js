/* KAKU WORK TRACKER - shared core logic (used by the app and by node tests) */
'use strict';
const STATUSES=['Present','Absent','Half Day','Leave','Holiday','Sunday Off'];
const SCOLORS={Present:'#34d399',Absent:'#f87171','Half Day':'#fbbf24',Leave:'#60a5fa',Holiday:'#a78bfa','Sunday Off':'#94a3b8'};
const MONTHS=['January','February','March','April','May','June','July','August','September','October','November','December'];
const LEAVE_TYPES=['Casual','Sick','Earned / Paid','Unpaid','Other'];

function istToday(){return new Intl.DateTimeFormat('en-CA',{timeZone:'Asia/Kolkata'}).format(new Date())}
function dayName(ds){const[y,m,d]=ds.split('-').map(Number);return ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'][new Date(y,m-1,d).getDay()]}
function istTs(){const p=new Intl.DateTimeFormat('en-GB',{timeZone:'Asia/Kolkata',year:'numeric',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',hourCycle:'h23'}).formatToParts(new Date());const g=t=>p.find(x=>x.type===t).value;return g('year')+'-'+g('month')+'-'+g('day')+' '+g('hour')+':'+g('minute')+' IST'}
function achv(p,t){if(p===''||p==null||t===''||t==null||Number(t)===0)return null;return Number(p)/Number(t)}
function fmtPct(x){return x==null?'-':(x*100).toFixed(1)+'%'}
function esc(s){return String(s==null?'':s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
function escCsv(v){return '"'+String(v==null?'':v).replace(/"/g,'""')+'"'}
function monthKey(ds){return ds.slice(0,7)}

function agg(list){
  const a={present:0,absent:0,half:0,leave:0,holiday:0,sunday:0,hours:0,ot:0,prod:0,target:0,n:0};
  list.forEach(r=>{a.n++;
    if(r.status==='Present')a.present++;else if(r.status==='Absent')a.absent++;else if(r.status==='Half Day')a.half++;
    else if(r.status==='Leave')a.leave++;else if(r.status==='Holiday')a.holiday++;else if(r.status==='Sunday Off')a.sunday++;
    a.hours+=Number(r.hours||0);a.ot+=Number(r.ot||0);a.prod+=Number(r.prod||0);a.target+=Number(r.target||0)});
  a.achv=a.target?achv(a.prod,a.target):null;return a;
}

const DATE_RE=/^\d{4}-\d{2}-\d{2}$/;
function validDate(ds){if(!DATE_RE.test(ds))return false;const[y,m,d]=ds.split('-').map(Number);const dt=new Date(y,m-1,d);return dt.getFullYear()===y&&dt.getMonth()===m-1&&dt.getDate()===d}
function numOk(v,min,max){if(v===''||v==null)return true;const n=Number(v);return Number.isFinite(n)&&n>=min&&n<=max}
function validateRecord(r){
  const e=[];
  if(!validDate(String(r.date||'')))e.push('date');
  if(STATUSES.indexOf(r.status)<0)e.push('status');
  if(r.shift&&['A','B','C'].indexOf(r.shift)<0)e.push('shift');
  if(!numOk(r.hours,0,24))e.push('hours');
  if(!numOk(r.ot,0,24))e.push('ot');
  if(!numOk(r.prod,0,10000000))e.push('production');
  if(!numOk(r.target,0,10000000))e.push('target');
  if(r.leaveType&&LEAVE_TYPES.indexOf(r.leaveType)<0)e.push('leaveType');
  if(String(r.remarks||'').length>500)e.push('remarks length');
  if(String(r.holidayName||'').length>80)e.push('holiday name length');
  return {ok:e.length===0,errors:e};
}

/* Merge server rows into local records: newer "updated" stamp wins, everything from the server is marked synced. Returns count applied. */
function mergePulled(recs,srv){
  let n=0;
  (srv||[]).forEach(sr=>{
    if(!validDate(String(sr.date||'')))return;
    const k=sr.date,lo=recs[k];
    if(!lo||String(lo.updated||'')<String(sr.updated||'')){recs[k]=Object.assign({},sr,{synced:true});n++}
    else recs[k].synced=true;
  });
  return n;
}

/* Sample data for ?demo=1 preview. Never written anywhere; sync is disabled in demo mode. */
function makeDemo(){
  const rec={};
  const put=(ds,status,shift,h,ot,p,t,extra)=>{rec[ds]=Object.assign({date:ds,day:dayName(ds),status:status,shift:shift||'',hours:h===''?'':h,ot:ot===''?'':ot,prod:p===''?'':p,target:t===''?'':t,remarks:'',updated:'2026-11-08 09:00 IST',synced:true,demo:true},extra||{})};
  put('2026-11-01','Sunday Off','','','','','');
  put('2026-11-02','Present','B',8,0.5,190,180);put('2026-11-03','Present','B',8,0,175,180);put('2026-11-04','Present','B',8,1,200,180);
  put('2026-11-05','Half Day','B',4,0,90,90);put('2026-11-06','Present','B',8,0,180,180);
  put('2026-11-07','Holiday','','','','','',{holidayName:'Company holiday (demo)'});
  put('2026-11-08','Sunday Off','','','','','');
  put('2026-11-09','Holiday','','','','','',{holidayName:'Govardhan Puja'});
  put('2026-11-10','Present','A',8,0,210,200);put('2026-11-11','Present','A',8,1,225,200);
  return rec;
}

if(typeof module!=='undefined'&&module.exports){module.exports={STATUSES,SCOLORS,MONTHS,LEAVE_TYPES,istToday,dayName,istTs,achv,fmtPct,esc,escCsv,monthKey,agg,validDate,validateRecord,mergePulled,makeDemo}}
