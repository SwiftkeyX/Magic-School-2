/**
 * Delete every RESOLVED comment on the tft-set9-skill sheet.
 *
 * WHY THIS EXISTS AS A SCRIPT YOU RUN, rather than something the sync tooling does: the Drive API
 * only lets an account delete comments it AUTHORED, or any comment if it OWNS the file. The project
 * service account (magic-school-sync@...) has edit access but is neither, so deleting your comments
 * returns 403. This runs as YOU, so it can.
 *
 * HOW TO RUN
 *   1. script.google.com -> New project -> paste this file.
 *   2. Services (+) -> Drive API -> Add.  (Advanced service, identifier `Drive`.)
 *   3. Run `listResolved` FIRST — it deletes nothing and prints what would go.
 *   4. Run `deleteResolved` when the count looks right. THIS IS PERMANENT.
 *
 * Every thread is archived at .claude/docs/tft/set9-skill-review-comments-archive.md, so the record
 * survives regardless. Open threads are never touched.
 */

var FILE_ID = '1X5glHjVcgv3yYG4Q2SyV9YJS3sv_wH5XAg3RLOHnUa4';

function fetchAll_() {
  var out = [], token = null;
  do {
    var res = Drive.Comments.list(FILE_ID, {
      fields: 'nextPageToken,comments(id,resolved,content,quotedFileContent/value)',
      pageSize: 100, pageToken: token, includeDeleted: false
    });
    out = out.concat(res.comments || []);
    token = res.nextPageToken;
  } while (token);
  return out;
}

function listResolved() {
  var all = fetchAll_();
  var res = all.filter(function (c) { return c.resolved; });
  Logger.log('%s threads total — %s resolved, %s open', all.length, res.length,
             all.length - res.length);
  res.forEach(function (c, i) {
    Logger.log('%s. %s', i + 1, (c.content || '').substring(0, 70).replace(/
/g, ' '));
  });
  Logger.log('Nothing deleted. Run deleteResolved() to delete these %s.', res.length);
}

function deleteResolved() {
  var res = fetchAll_().filter(function (c) { return c.resolved; });
  var ok = 0, fail = 0;
  res.forEach(function (c) {
    try { Drive.Comments.remove(FILE_ID, c.id); ok++; }
    catch (e) { fail++; Logger.log('failed %s: %s', c.id, e.message); }
  });
  Logger.log('deleted %s of %s resolved threads (%s failed)', ok, res.length, fail);
}
