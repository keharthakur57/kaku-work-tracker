import re
p='/workspace/kwt/index.html'
s=open(p,encoding='utf-8').read()

CSS="""<style>
:root{--bg:#0c0918;--bg2:#16102e;--card:#1c1638;--card2:#241c4a;--line:#352b63;--txt:#f3f0fc;--mut:#b0a6d6;
--acc:#8b5cf6;--acc2:#a78bfa;--accgrad:linear-gradient(135deg,#8b5cf6,#6d28d9);
--ok:#34d399;--warn:#fbbf24;--bad:#f87171;--blue:#60a5fa;--gray:#94a3b8;--r:18px;
--shadow:0 8px 28px rgba(6,3,18,.45)}
*{box-sizing:border-box;margin:0;padding:0;-webkit-tap-highlight-color:transparent}
html,body{height:100%}
body{background:radial-gradient(900px 500px at 85% -5%,#2b1e5e 0%,transparent 55%),radial-gradient(700px 420px at -10% 15%,#221a48 0%,transparent 50%),var(--bg);color:var(--txt);font-family:system-ui,-apple-system,'Segoe UI',Roboto,sans-serif;font-size:15px;line-height:1.5;-webkit-font-smoothing:antialiased}
#appwrap{max-width:580px;margin:0 auto;min-height:100%;padding-bottom:96px;position:relative}
:focus-visible{outline:2px solid var(--acc2);outline-offset:2px;border-radius:8px}
@media (prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}}
header.top{position:sticky;top:0;z-index:20;background:rgba(16,11,36,.88);backdrop-filter:blur(12px);padding:14px 16px 12px;border-bottom:1px solid var(--line);display:flex;align-items:center;justify-content:space-between;gap:8px}
header.top h1{font-size:16px;font-weight:800;letter-spacing:.5px}
header.top h1 span{color:var(--acc2)}
.hdrbtns{display:flex;gap:8px;align-items:center}
.badge{font-size:11px;font-weight:700;padding:4px 10px;border-radius:99px;background:#31265e;color:var(--mut);white-space:nowrap}
.badge.warn{background:#4a3a12;color:var(--warn)}
.badge.ok{background:#123a2b;color:var(--ok)}
.iconbtn{background:var(--card2);border:1px solid var(--line);color:var(--txt);border-radius:12px;padding:9px 12px;font-size:15px;cursor:pointer;min-height:40px}
main{padding:14px 14px 0}
.page{display:none}
.page.on{display:block;animation:fade .18s ease}
@keyframes fade{from{opacity:0;transform:translateY(4px)}to{opacity:1;transform:none}}
.card{background:linear-gradient(180deg,var(--card),var(--card) 60%,#191334);border:1px solid var(--line);border-radius:var(--r);padding:16px;margin-bottom:12px;box-shadow:var(--shadow)}
.card h2{font-size:12px;text-transform:uppercase;letter-spacing:1.2px;color:var(--mut);margin-bottom:12px;font-weight:700}
.hero{background:linear-gradient(135deg,#2b2058,#1c1440 65%);border:1px solid #4a3a8a}
.herotop{display:flex;align-items:flex-start;justify-content:space-between;gap:10px}
.hello{font-size:20px;font-weight:800}
.hello .wave{font-size:18px}
.herodate{color:var(--mut);font-size:13px;margin-top:2px}
.heroshift{text-align:right;font-size:0}
.herostats{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:14px}
.row{display:flex;gap:10px}
.row>*{flex:1;min-width:0}
label{display:block;font-size:12.5px;color:var(--mut);margin:10px 0 5px;font-weight:600}
label.chk{display:flex;align-items:center;gap:8px;font-size:13px;color:var(--txt);margin:10px 0 2px}
input,select,textarea{width:100%;background:var(--bg2);border:1px solid var(--line);border-radius:12px;color:var(--txt);padding:13px;font-size:15px;outline:none;font-family:inherit}
input:focus,select:focus,textarea:focus{border-color:var(--acc);box-shadow:0 0 0 3px rgba(139,92,246,.25)}
textarea{resize:vertical;min-height:64px}
.chips{display:flex;flex-wrap:wrap;gap:8px}
.chip{border:1px solid var(--line);background:var(--bg2);color:var(--txt);border-radius:99px;padding:10px 15px;font-size:13.5px;font-weight:600;cursor:pointer;min-height:42px}
.chip.sel{background:var(--acc);border-color:var(--acc);color:#fff}
.chip.s-Present.sel{background:var(--ok);border-color:var(--ok);color:#052e1e}
.chip.s-Absent.sel{background:var(--bad);border-color:var(--bad);color:#2b0705}
.chip.s-HalfDay.sel{background:var(--warn);border-color:var(--warn);color:#3a2a05}
.btn{display:inline-block;background:var(--accgrad);color:#fff;border:0;border-radius:14px;padding:14px 18px;font-size:15px;font-weight:700;cursor:pointer;width:100%;text-align:center;box-shadow:0 4px 16px rgba(109,40,217,.35)}
.btn.sec{background:var(--card2);border:1px solid var(--line);color:var(--txt);box-shadow:none}
.btn.sm{width:auto;padding:10px 15px;font-size:13.5px;border-radius:12px;min-height:42px}
.btn:disabled{opacity:.5}
.kv{display:flex;justify-content:space-between;padding:9px 0;border-bottom:1px solid rgba(53,43,99,.6);font-size:14px;gap:10px}
.kv:last-child{border-bottom:0}
.kv b{font-weight:700;text-align:right}
.stat{background:rgba(22,16,46,.85);border:1px solid var(--line);border-radius:14px;padding:12px;text-align:center}
.stat .v{font-size:20px;font-weight:800}
.stat .l{font-size:11px;color:var(--mut);margin-top:2px}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.grid3{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}
nav.bottom{position:fixed;bottom:0;left:0;right:0;z-index:30;background:rgba(20,14,44,.95);backdrop-filter:blur(10px);border-top:1px solid var(--line);display:flex;justify-content:space-around;max-width:580px;margin:0 auto;padding:6px 4px calc(8px + env(safe-area-inset-bottom))}
nav.bottom button{flex:1;background:0;border:0;color:var(--mut);font-size:10.5px;font-weight:600;padding:6px 2px;cursor:pointer;border-radius:10px;display:flex;flex-direction:column;align-items:center;gap:3px;min-height:48px}
nav.bottom button .i{font-size:19px}
nav.bottom button.on{color:var(--acc2);background:#2a2154}
.cal{display:grid;grid-template-columns:repeat(7,1fr);gap:5px;margin-top:8px}
.cal .h{font-size:10px;color:var(--mut);text-align:center;font-weight:700;padding:4px 0}
.cal .d{aspect-ratio:1;border-radius:12px;background:var(--bg2);border:1px solid var(--line);display:flex;flex-direction:column;align-items:center;justify-content:center;font-size:13px;cursor:pointer;position:relative}
.cal .d:hover{border-color:var(--acc)}
.cal .d.dim{opacity:.3}
.cal .d.today{border-color:var(--acc);border-width:2px;box-shadow:0 0 0 3px rgba(139,92,246,.2)}
.cal .d .dot{width:8px;height:8px;border-radius:99px;margin-top:2px}
.mnav{display:flex;align-items:center;justify-content:space-between;margin-bottom:6px}
.mnav b{font-size:15px}
.tblwrap{overflow-x:auto;-webkit-overflow-scrolling:touch;border-radius:10px}
table{width:100%;border-collapse:collapse;font-size:13px}
th,td{padding:9px 6px;border-bottom:1px solid var(--line);text-align:left;white-space:nowrap}
th{color:var(--mut);font-size:11px;text-transform:uppercase;letter-spacing:.5px}
td.num,th.num{text-align:right}
.pill{font-size:11px;font-weight:700;padding:4px 10px;border-radius:99px;display:inline-block}
.pill.st-Present{background:rgba(52,211,153,.18);color:var(--ok)}
.pill.st-Absent{background:rgba(248,113,113,.18);color:var(--bad)}
.pill.st-HalfDay{background:rgba(251,191,36,.18);color:var(--warn)}
.pill.st-Leave{background:rgba(96,165,250,.18);color:var(--blue)}
.pill.st-Holiday{background:rgba(167,139,250,.18);color:var(--acc2)}
.pill.st-SundayOff{background:rgba(148,163,184,.18);color:var(--gray)}
.pill.shift{background:var(--card2);color:var(--txt);margin-left:4px}
.pill.pend{background:rgba(251,191,36,.18);color:var(--warn)}
canvas{width:100%;height:auto;display:block}
.syncnote{font-size:12px;color:var(--mut);margin-top:8px}
.qitem{display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid var(--line);font-size:13px;gap:10px}
.hint{font-size:12.5px;color:var(--mut);margin-top:6px}
.hint.warn{color:var(--warn)}
.empty{padding:18px 10px;text-align:center;color:var(--mut);font-size:13.5px}
.toast{position:fixed;left:50%;transform:translateX(-50%);bottom:104px;background:#2f2560;color:#fff;padding:12px 18px;border-radius:14px;font-size:13.5px;font-weight:600;z-index:60;box-shadow:0 8px 28px rgba(0,0,0,.55);display:none;max-width:88%;text-align:center}
.err{color:var(--bad);font-size:13px;margin-top:8px;display:none}
#authscreen{position:fixed;inset:0;z-index:50;background:radial-gradient(1100px 620px at 50% -10%,#33246b,#0c0918 62%);display:flex;align-items:center;justify-content:center;padding:20px}
.authcard{width:100%;max-width:400px;background:var(--card);border:1px solid var(--line);border-radius:22px;padding:26px 22px;box-shadow:0 20px 60px rgba(0,0,0,.5)}
.authcard h1{font-size:21px;font-weight:800;margin-bottom:4px}
.authcard h1 span{color:var(--acc2)}
.authcard p{color:var(--mut);font-size:13px;margin-bottom:16px}
.biglogo{width:64px;height:64px;border-radius:18px;background:var(--accgrad);display:flex;align-items:center;justify-content:center;font-size:26px;font-weight:800;margin-bottom:14px;box-shadow:0 8px 24px rgba(109,40,217,.4)}
details summary{cursor:pointer;color:var(--acc2);font-size:13px;font-weight:600;margin-top:8px}
pre.code{background:#120d29;border:1px solid var(--line);border-radius:12px;padding:10px;font-size:11px;overflow-x:auto;max-height:180px;overflow-y:auto;white-space:pre}
ol.steps{padding-left:18px;font-size:13px;color:var(--mut)}
ol.steps li{margin-bottom:6px}
@media (min-width:600px){main{padding:18px 18px 0}.card{padding:18px}}
</style>"""
m=re.search(r"<style>.*?</style>",s,re.S)
assert m
s=s[:m.start()]+CSS+s[m.end():]

# label-for association pass (labels immediately followed by an input/select/textarea carrying an id)
def labfor(m):
    return '<label for="%s">%s</label>%s<%s%s id="%s"'%(m.group(5),m.group(1),m.group(2),m.group(3),m.group(4),m.group(5))
s2,n=re.subn(r'<label>([^<]+)</label>(\s*)<(input|select|textarea)([^>]*?)\s*id="([A-Za-z0-9_-]+)"',labfor,s)
print('label-for pairs linked:',n)
# avoid double id from greedy attr match
s=s.replace(' id=""','')

# sync secret input: paste-once model + remember checkbox
old='<label for="s-secret">Sync secret (any private phrase, set once)</label><input id="s-secret" type="password" placeholder="Private phrase">'
if old not in s:
    old='<label>Sync secret (any private phrase, set once)</label><input id="s-secret" type="password" placeholder="Private phrase">'
assert old in s, 'secret input not found'
s=s.replace(old,'<label for="s-secret">Sync secret (from the Apps Script log, shown once)</label><input id="s-secret" type="password" autocomplete="off" placeholder="Paste the secret here">\n      <label class="chk"><input type="checkbox" id="s-remember" style="width:auto"> Keep secret on this device (less safe)</label>')

# guided deploy steps: provision-first flow
m=re.search(r'<ol class="steps">.*?</ol>',s,re.S)
assert m
s=s[:m.start()]+"""<ol class="steps">
          <li>Open your Google Sheet &rarr; <b>Extensions &rarr; Apps Script</b>.</li>
          <li>Delete any code there, paste the KAKU backend code below, and save.</li>
          <li>In the editor select <b>kwtProvision</b> and click Run. Approve the permissions, then <b>View &rarr; Logs</b> and copy the secret it created.</li>
          <li><b>Deploy &rarr; New deployment &rarr; Web app</b>. Execute as: <b>Me</b>. Who has access: <b>Anyone</b>. Deploy.</li>
          <li>Paste the Web app URL and your secret above, then Test connection.</li>
        </ol>"""+s[m.end():]

# security note after the steps details block
assert s.count('</ol>')==1, s.count('</ol>')
i=s.index('</ol>')+len('</ol>')
s=s[:i]+'<p class="hint warn">Security note: "Execute as Me + Anyone" means anyone holding both the web app URL and your secret can write to your sheet. The URL alone can do nothing until you run kwtProvision once, and only you (the sheet owner) can run it. Keep the secret private; rotate it any time with kwtRotateSecret.</p>'+s[i:]
open(p,'w',encoding='utf-8').write(s)
print('patch2 OK, size',len(s))
