import quickjs, json, sys

core = open('/workspace/kwt/js/core.js').read()
ctx = quickjs.Context()
ctx.eval("var module={exports:{}};")
try:
    ctx.eval(core)
except Exception as e:
    print('LOAD FAIL:', e); sys.exit(1)

harness = """
var __r=[];
function t(n,f){try{f();__r.push('PASS '+n)}catch(e){__r.push('FAIL '+n+': '+e.message)}}
function eq(a,b){if(a!==b)throw new Error('got '+JSON.stringify(a)+' want '+JSON.stringify(b))}
function deep(a,b){if(JSON.stringify(a)!==JSON.stringify(b))throw new Error('got '+JSON.stringify(a)+' want '+JSON.stringify(b))}
var C=module.exports;
t('dayName Sunday',function(){eq(C.dayName('2026-11-08'),'Sunday')});
t('dayName Tuesday',function(){eq(C.dayName('2026-11-10'),'Tuesday')});
t('dayName leap',function(){eq(C.dayName('2028-02-29'),'Tuesday')});
t('achv normal',function(){eq(C.achv(210,200),1.05)});
t('achv exact',function(){eq(C.achv(180,180),1)});
t('achv zero target',function(){eq(C.achv(180,0),null)});
t('achv empty prod',function(){eq(C.achv('',200),null)});
t('achv strings',function(){eq(C.achv('105','100'),1.05)});
t('fmtPct',function(){eq(C.fmtPct(1),'100.0%');eq(C.fmtPct(null),'-');eq(C.fmtPct(0.855),'85.5%')});
t('esc',function(){eq(C.esc('<b>&"\\''),"&lt;b&gt;&amp;&quot;&#39;")});
t('escCsv',function(){eq(C.escCsv('say "hi"'),'\"say \"\"hi\"\"\"');eq(C.escCsv(null),'\"\"')});
t('monthKey',function(){eq(C.monthKey('2026-11-08'),'2026-11')});
t('validDate rejects',function(){eq(C.validDate('2026-02-30'),false);eq(C.validDate('2026-13-01'),false);eq(C.validDate('abc'),false);eq(C.validDate('2026-2-3'),false)});
t('validDate accepts',function(){eq(C.validDate('2026-02-28'),true);eq(C.validDate('2028-02-29'),true)});
t('agg sums and classes',function(){
  var a=C.agg([{status:'Present',hours:'8',ot:1,prod:200,target:200},{status:'Half Day',hours:4,ot:'',prod:90,target:90},{status:'Sunday Off',hours:'',ot:'',prod:'',target:''}]);
  deep([a.present,a.half,a.sunday,a.n],[1,1,1,3]);deep([a.hours,a.ot,a.prod,a.target],[12,1,290,290]);eq(C.fmtPct(a.achv),'100.0%')});
t('agg empty',function(){eq(C.agg([]).achv,null)});
t('validate accepts',function(){var v=C.validateRecord({date:'2026-11-10',status:'Present',shift:'A',hours:8,ot:0,prod:210,target:200,remarks:'ok'});if(!v.ok)throw new Error(v.errors.join(','))});
t('validate rejects',function(){
  var v=C.validateRecord({date:'2026-02-30',status:'Maybe',shift:'D',hours:30,ot:-1,prod:'x',target:200});
  ['date','status','shift','hours','ot','production'].forEach(function(f){if(v.errors.indexOf(f)<0)throw new Error('missing '+f)})});
t('validate off-day',function(){var v=C.validateRecord({date:'2026-11-08',status:'Sunday Off'});if(!v.ok)throw new Error(v.errors.join(','))});
t('merge newer server wins',function(){var recs={'2026-11-10':{date:'2026-11-10',status:'Present',updated:'2026-11-10 15:00 IST',synced:false}};
  var n=C.mergePulled(recs,[{date:'2026-11-10',status:'Absent',updated:'2026-11-10 16:00 IST'}]);
  eq(n,1);eq(recs['2026-11-10'].status,'Absent');eq(recs['2026-11-10'].synced,true)});
t('merge newer local kept',function(){var recs={'2026-11-10':{date:'2026-11-10',status:'Present',updated:'2026-11-10 17:00 IST',synced:false}};
  var n=C.mergePulled(recs,[{date:'2026-11-10',status:'Absent',updated:'2026-11-10 16:00 IST'}]);
  eq(n,0);eq(recs['2026-11-10'].status,'Present');eq(recs['2026-11-10'].synced,true)});
t('merge adds new',function(){var recs={};var n=C.mergePulled(recs,[{date:'2026-11-11',status:'Leave',updated:'2026-11-11 10:00 IST'}]);
  eq(n,1);eq(recs['2026-11-11'].status,'Leave')});
t('merge skips bad dates',function(){var recs={};var n=C.mergePulled(recs,[{date:'nope',status:'Present'}]);
  eq(n,0);eq(Object.keys(recs).length,0)});
t('demo well-formed',function(){var d=C.makeDemo();var ks=Object.keys(d);
  if(ks.length<8)throw new Error('too few');
  ks.forEach(function(k){var v=C.validateRecord(d[k]);if(!v.ok)throw new Error(k+': '+v.errors);if(!d[k].demo)throw new Error('not demo')})});
t('demo colors',function(){var d=C.makeDemo();Object.keys(d).forEach(function(k){if(!C.SCOLORS[d[k].status])throw new Error('no color '+d[k].status)})});
return JSON.stringify(__r);
"""
res = json.loads(ctx.eval("(function(){\n"+harness+"\n})()"))
for line in res: print(line)
fails = [l for l in res if l.startswith('FAIL')]
print('SUITE:', 'ALL PASS (%d tests)' % len(res) if not fails else 'FAILED (%d)' % len(fails))
sys.exit(1 if fails else 0)
