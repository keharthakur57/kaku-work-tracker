/**
 * KAKU WORK TRACKER - Sheets backend (hardened, v2)
 *
 * SETUP (sheet owner only, about 2 minutes):
 *  1. Sheet -> Extensions -> Apps Script. Delete any code, paste this file, save.
 *  2. Select kwtProvision in the function list and click Run. Approve permissions.
 *     Then View -> Logs: copy the secret it created (shown once).
 *  3. Deploy -> New deployment -> Web app. Execute as: Me. Who has access: Anyone. Deploy.
 *  4. In the app's Settings: paste the Web app URL + the secret, Test connection.
 *
 * SECURITY MODEL (read this):
 *  - "Execute as Me + Anyone" exposes a public URL. The URL alone can do nothing:
 *    every request must carry the secret created by kwtProvision (editor access
 *    is owner-only, so only you can create or rotate it).
 *  - Requests are replay-protected (timestamp + one-time nonce, 5-minute window)
 *    and rate-limited (30 requests/minute).
 *  - Inputs are validated; nothing outside this workbook is touched.
 *  - This is a shared-secret model, not real user authentication. Do not share
 *    the secret. Rotate any time with kwtRotateSecret().
 */
var TZ = 'Asia/Kolkata';
var SS = SpreadsheetApp.getActiveSpreadsheet();
var MAX_RECORDS = 50, MAX_TEXT = 500, MAX_HOL = 80;
var RATE_LIMIT = 30, RATE_WINDOW_MS = 60000, REPLAY_WINDOW_MS = 300000;
var STATUSES = ['Present', 'Absent', 'Half Day', 'Leave', 'Holiday', 'Sunday Off'];
var SHIFTS = ['A', 'B', 'C'];
var LEAVE_TYPES = ['Casual', 'Sick', 'Earned / Paid', 'Unpaid', 'Other'];

function json_(o){ return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON); }
function normDate_(v){
  if (v instanceof Date) return Utilities.formatDate(v, TZ, 'yyyy-MM-dd');
  return String(v == null ? '' : v).trim().slice(0, 10);
}
function validDate_(ds){ if (!/^\d{4}-\d{2}-\d{2}$/.test(ds)) return false;
  var p = ds.split('-'), y = +p[0], m = +p[1], d = +p[2];
  if (m < 1 || m > 12 || d < 1 || d > 31) return false;
  var dt = new Date(Date.UTC(y, m - 1, d));
  return dt.getUTCFullYear() === y && dt.getUTCMonth() === m - 1 && dt.getUTCDate() === d; }
function num_(x, min, max){ if (x === '' || x == null) return ''; var n = Number(x);
  if (!isFinite(n) || n < min || n > max) return ''; return n; }
function nowIst_(){ return Utilities.formatDate(new Date(), TZ, 'yyyy-MM-dd HH:mm') + ' IST'; }
function clamp_(v, max){ v = String(v == null ? '' : v); return v.length > max ? v.slice(0, max) : v; }

function doGet(){ return json_({ok: true, app: 'KAKU WORK TRACKER backend', time: nowIst_()}); }

/* Owner-only provisioning: run from the Apps Script editor. */
function kwtProvision(){
  var p = PropertiesService.getScriptProperties();
  if (p.getProperty('KWT_SECRET')) return 'Secret already provisioned. To replace it, run kwtRotateSecret().';
  var s = 'kwt-' + Utilities.getUuid() + Utilities.getUuid();
  p.setProperty('KWT_SECRET', s);
  Logger.log('KWT_SECRET (copy into the app Settings, shown once): ' + s);
  return 'Secret created. Open View > Logs (or the execution log) to copy it, then delete the log entry.';
}
function kwtRotateSecret(){
  var p = PropertiesService.getScriptProperties();
  var s = 'kwt-' + Utilities.getUuid() + Utilities.getUuid();
  p.setProperty('KWT_SECRET', s);
  CacheService.getScriptCache().removeAll(['kwt_nonces']);
  Logger.log('NEW KWT_SECRET (update the app Settings): ' + s);
  return 'Rotated. Copy the new secret from the log into the app.';
}

function rateOk_(){
  var c = CacheService.getScriptCache();
  var win = Math.floor(Date.now() / RATE_WINDOW_MS);
  var k = 'kwt_rl_' + win;
  var n = Number(c.get(k) || 0);
  if (n >= RATE_LIMIT) return false;
  c.put(k, String(n + 1), 300);
  return true;
}
function replayOk_(body){
  var ts = Number(body.ts || 0), nonce = String(body.nonce || '');
  if (!ts || !nonce) return false;
  if (Math.abs(Date.now() - ts) > REPLAY_WINDOW_MS) return false;
  var c = CacheService.getScriptCache();
  var k = 'kwt_nonce_' + nonce;
  if (c.get(k)) return false;
  c.put(k, '1', 21600); /* CacheService max TTL: 6 hours */
  return true;
}

function doPost(e){
  try{
    var body = JSON.parse(e.postData.contents || '{}');
    var secret = PropertiesService.getScriptProperties().getProperty('KWT_SECRET');
    if (!secret) return json_({ok: false, error: 'Backend not provisioned. The sheet owner must run kwtProvision() once in the Apps Script editor.'});
    if (!body.secret || body.secret !== secret) return json_({ok: false, error: 'bad secret'});
    if (!rateOk_()) return json_({ok: false, error: 'Too many requests. Try again in a minute.'});
    if (!replayOk_(body)) return json_({ok: false, error: 'Stale or repeated request. Check the device clock and retry.'});
    if (body.action === 'ping') return json_({ok: true, time: nowIst_()});
    if (body.action === 'getAll') return getAll_();
    if (body.action === 'upsert') return upsert_(body.records || []);
    return json_({ok: false, error: 'unknown action'});
  }catch(err){ return json_({ok: false, error: String(err && err.message || err)}); }
}

function findRow_(sheet, dateStr){
  var last = sheet.getLastRow();
  if (last < 2) return -1;
  var vals = sheet.getRange(2, 1, last - 1, 1).getValues();
  for (var i = 0; i < vals.length; i++){ if (normDate_(vals[i][0]) === dateStr) return i + 2; }
  return -1;
}

function validate_(r){
  var ds = normDate_(r.date);
  if (!validDate_(ds)) return 'bad date';
  if (STATUSES.indexOf(r.status) < 0) return 'bad status';
  if (r.shift && SHIFTS.indexOf(r.shift) < 0) return 'bad shift';
  if (num_(r.hours, 0, 24) === '' && r.hours !== '' && r.hours != null) return 'bad hours';
  if (num_(r.ot, 0, 24) === '' && r.ot !== '' && r.ot != null) return 'bad ot';
  if (num_(r.prod, 0, 10000000) === '' && r.prod !== '' && r.prod != null) return 'bad production';
  if (num_(r.target, 0, 10000000) === '' && r.target !== '' && r.target != null) return 'bad target';
  if (r.leaveType && LEAVE_TYPES.indexOf(r.leaveType) < 0) return 'bad leave type';
  return null;
}

function upsert_(recs){
  if (!recs || !recs.length) return json_({ok: false, error: 'no records'});
  if (recs.length > MAX_RECORDS) return json_({ok: false, error: 'too many records in one request (max ' + MAX_RECORDS + ')'});
  var daily = SS.getSheetByName('Daily Attendance');
  var prod = SS.getSheetByName('Production Performance');
  var hist = SS.getSheetByName('Edit History');
  var leaves = SS.getSheetByName('Leave Records');
  var hols = SS.getSheetByName('Holiday Records');
  var saved = 0, rejected = [];
  recs.forEach(function(r){
    var why = validate_(r);
    if (why){ rejected.push({date: normDate_(r.date), reason: why}); return; }
    var ds = normDate_(r.date);
    var row = findRow_(daily, ds);
    var isNew = row < 1;
    var oldSummary = '';
    if (!isNew){
      var old = daily.getRange(row, 1, 1, 12).getValues()[0];
      oldSummary = 'status=' + old[1] + ', shift=' + old[2] + ', hrs=' + old[3] + ', ot=' + old[4] + ', prod=' + old[5] + ', target=' + old[6] + ', remarks=' + old[8];
    }
    var vals = [new Date(ds), r.status, r.shift || '', num_(r.hours, 0, 24), num_(r.ot, 0, 24),
                num_(r.prod, 0, 10000000), num_(r.target, 0, 10000000)];
    var trow = isNew ? daily.getLastRow() + 1 : row;
    daily.getRange(trow, 1, 1, 7).setValues([vals]);
    daily.getRange(trow, 9).setValue(clamp_(r.remarks, MAX_TEXT));
    daily.getRange(trow, 11).setValue(nowIst_());
    daily.getRange(trow, 12).setValue('Web App');
    if ((r.prod !== '' && r.prod != null) || (r.target !== '' && r.target != null)){
      var prow = findRow_(prod, ds);
      var pr = prow > 0 ? prow : prod.getLastRow() + 1;
      prod.getRange(pr, 1).setValue(new Date(ds));
      prod.getRange(pr, 2).setValue(num_(r.prod, 0, 10000000));
      prod.getRange(pr, 3).setValue(num_(r.target, 0, 10000000));
    }
    if (r.leaveType){
      var lrow = findRow_(leaves, ds);
      var lr = lrow > 0 ? lrow : leaves.getLastRow() + 1;
      leaves.getRange(lr, 1, 1, 3).setValues([[new Date(ds), new Date(ds), r.leaveType]]);
      leaves.getRange(lr, 4).setValue('Web App');
      leaves.getRange(lr, 5).setValue(clamp_(r.remarks, MAX_TEXT));
    }
    if (r.holidayName){
      var hrow = findRow_(hols, ds);
      var hr = hrow > 0 ? hrow : hols.getLastRow() + 1;
      hols.getRange(hr, 1, 1, 4).setValues([[new Date(ds), clamp_(r.holidayName, MAX_HOL), '', 'Web App']]);
    }
    hist.appendRow([nowIst_(), new Date(ds), isNew ? 'created (web app)' : 'updated (web app)',
      oldSummary,
      'status=' + (r.status || '') + ', shift=' + (r.shift || '') + ', hrs=' + (r.hours || '') + ', ot=' + (r.ot || '') + ', prod=' + (r.prod || '') + ', target=' + (r.target || '') + ((r.leaveType) ? ', leave=' + r.leaveType : '') + ((r.holidayName) ? ', holiday=' + r.holidayName : '') + ((r.remarks) ? ', remarks=' + clamp_(r.remarks, 120) : ''),
      'Web App']);
    saved++;
  });
  return json_({ok: true, saved: saved, rejected: rejected, time: nowIst_()});
}

function getAll_(){
  var daily = SS.getSheetByName('Daily Attendance');
  var last = daily.getLastRow();
  var out = [];
  if (last >= 2){
    var vals = daily.getRange(2, 1, Math.min(last, 500), 12).getValues();
    vals.forEach(function(v){
      var ds = normDate_(v[0]); if (!ds) return;
      out.push({date: ds, day: '', status: String(v[1] || ''), shift: String(v[2] || ''),
        hours: num_(v[3], 0, 24), ot: num_(v[4], 0, 24), prod: num_(v[5], 0, 10000000), target: num_(v[6], 0, 10000000),
        remarks: String(v[8] || ''), updated: String(v[10] || '')});
    });
  }
  return json_({ok: true, records: out, time: nowIst_()});
}
