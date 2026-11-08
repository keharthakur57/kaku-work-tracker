/**
 * KAKU WORK TRACKER - Sheets backend
 * Paste into: open the KAKU workbook -> Extensions -> Apps Script
 * Deploy: Deploy -> New deployment -> Web app
 *   Execute as: Me   |   Who has access: Anyone
 * The first request saves the secret you set in the app; after that
 * only requests carrying the same secret are accepted.
 */
var TZ = 'Asia/Kolkata';
var SS = SpreadsheetApp.getActiveSpreadsheet();

function json_(o){ return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON); }
function normDate_(v){
  if (v instanceof Date) return Utilities.formatDate(v, TZ, 'yyyy-MM-dd');
  return String(v == null ? '' : v).trim().slice(0, 10);
}
function num_(x){ if (x === '' || x == null) return ''; var n = Number(x); return isNaN(n) ? '' : n; }
function nowIst_(){ return Utilities.formatDate(new Date(), TZ, 'yyyy-MM-dd HH:mm') + ' IST'; }

function doGet(){ return json_({ok:true, app:'KAKU WORK TRACKER backend', time: nowIst_()}); }

function doPost(e){
  try{
    var body = JSON.parse(e.postData.contents);
    var props = PropertiesService.getScriptProperties();
    var secret = props.getProperty('KWT_SECRET');
    if (!secret){ props.setProperty('KWT_SECRET', String(body.secret || '')); secret = String(body.secret || ''); }
    if (!body.secret || body.secret !== secret) return json_({ok:false, error:'bad secret'});
    if (body.action === 'ping') return json_({ok:true, time: nowIst_()});
    if (body.action === 'getAll') return getAll_();
    if (body.action === 'upsert') return upsert_(body.records || []);
    return json_({ok:false, error:'unknown action'});
  }catch(err){ return json_({ok:false, error:String(err && err.message || err)}); }
}

function findRow_(sheet, dateStr){
  var last = sheet.getLastRow();
  if (last < 2) return -1;
  var vals = sheet.getRange(2, 1, last - 1, 1).getValues();
  for (var i = 0; i < vals.length; i++){ if (normDate_(vals[i][0]) === dateStr) return i + 2; }
  return -1;
}

function upsert_(recs){
  var daily = SS.getSheetByName('Daily Attendance');
  var prod = SS.getSheetByName('Production Performance');
  var hist = SS.getSheetByName('Edit History');
  var leaves = SS.getSheetByName('Leave Records');
  var hols = SS.getSheetByName('Holiday Records');
  var saved = 0;
  recs.forEach(function(r){
    var ds = normDate_(r.date); if (!ds) return;
    var row = findRow_(daily, ds);
    var isNew = row < 1;
    var oldSummary = '';
    if (!isNew){
      var old = daily.getRange(row, 1, 1, 12).getValues()[0];
      oldSummary = 'status=' + old[1] + ', shift=' + old[2] + ', hrs=' + old[3] + ', ot=' + old[4] + ', prod=' + old[5] + ', target=' + old[6];
    }
    var vals = [new Date(ds), r.status || '', r.shift || '', num_(r.hours), num_(r.ot), num_(r.prod), num_(r.target)];
    var trow = isNew ? daily.getLastRow() + 1 : row;
    daily.getRange(trow, 1, 1, 7).setValues([vals]);
    daily.getRange(trow, 9).setValue(r.remarks || '');
    daily.getRange(trow, 11).setValue(nowIst_());
    daily.getRange(trow, 12).setValue('Web App');
    if ((r.prod !== '' && r.prod != null) || (r.target !== '' && r.target != null)){
      var prow = findRow_(prod, ds);
      var pr = prow > 0 ? prow : prod.getLastRow() + 1;
      prod.getRange(pr, 1).setValue(new Date(ds));
      prod.getRange(pr, 2).setValue(num_(r.prod));
      prod.getRange(pr, 3).setValue(num_(r.target));
    }
    if (r.leaveType){
      var lrow = findRow_(leaves, ds);
      var lr = lrow > 0 ? lrow : leaves.getLastRow() + 1;
      leaves.getRange(lr, 1, 1, 3).setValues([[new Date(ds), new Date(ds), r.leaveType]]);
      leaves.getRange(lr, 4).setValue('Web App');
      leaves.getRange(lr, 5).setValue(r.remarks || '');
    }
    if (r.holidayName){
      var hrow = findRow_(hols, ds);
      var hr = hrow > 0 ? hrow : hols.getLastRow() + 1;
      hols.getRange(hr, 1, 1, 4).setValues([[new Date(ds), r.holidayName, '', 'Web App']]);
    }
    hist.appendRow([nowIst_(), new Date(ds), isNew ? 'created (web app)' : 'updated (web app)',
      oldSummary,
      'status=' + (r.status || '') + ', shift=' + (r.shift || '') + ', hrs=' + (r.hours || '') + ', ot=' + (r.ot || '') + ', prod=' + (r.prod || '') + ', target=' + (r.target || '') + ((r.leaveType) ? ', leave=' + r.leaveType : '') + ((r.holidayName) ? ', holiday=' + r.holidayName : ''),
      'Web App']);
    saved++;
  });
  return json_({ok:true, saved:saved, time: nowIst_()});
}

function getAll_(){
  var daily = SS.getSheetByName('Daily Attendance');
  var last = daily.getLastRow();
  var out = [];
  if (last >= 2){
    var vals = daily.getRange(2, 1, Math.min(last, 500), 12).getValues();
    vals.forEach(function(v){
      var ds = normDate_(v[0]); if (!ds) return;
      out.push({date:ds, day:'', status:String(v[1] || ''), shift:String(v[2] || ''),
        hours:num_(v[3]), ot:num_(v[4]), prod:num_(v[5]), target:num_(v[6]),
        remarks:String(v[8] || ''), updated:String(v[10] || '')});
    });
  }
  return json_({ok:true, records:out, time: nowIst_()});
}
