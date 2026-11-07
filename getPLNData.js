function getPLNData(){

  var stories = { local: {}, changes: {} };
  var locations = {};
  
  var props = PropertiesService.getScriptProperties();
  
  // We need to hold the data in batches by month.
  var locations = {};
  var pushStoryData = function(orig,type) {
    for (i = 0; i < orig.length; i++) {
      var s = orig[i];
      var d = new Date(s[1]);
      var m = d.getMonth() + 1;
      var y = d.getFullYear();
      var loc = s[0].trim();
      var coords = [s[3].trim(),s[4].trim()];
      if (!locations[loc]) locations[loc] = coords;
      if (!stories[type][y]) stories[type][y] = {};
      if (!stories[type][y][m]) stories[type][y][m] = [];
      stories[type][y][m].push([loc,s[1].trim(),s[2].replace(s[0].trim() + ' - ','').trim(),s[5].replace('http://www.publiclibrariesnews.com/','').trim()])
    }
  };
  pushStoryData(changes,'changes');
  pushStoryData(local,'local');
  var stories_file = DriveApp.createFile('PLNStories.json',JSON.stringify(stories))
  uploadFile(stories_file, 'PLNStories.json', props.getProperty('POST_TO_PLN'));
  uploadFile(stories_file, 'PLNStories.json', props.getProperty('POST_TO_NEWS'));
  DriveApp.removeFile(stories_file);
  
  var locFile = DriveApp.createFile('PLNLocations.json',JSON.stringify(locations))
  for (var storyType in stories){
    for (var year in stories[storyType]){
      for (var month in stories[storyType][year]){
        stories[storyType][year][month].sort(function(a, b) {
          a = new Date(a[1]);
          b = new Date(b[1]);
          return a < b;
        });
        var file = DriveApp.createFile('PLN_' + year + '_' + month + '_' + storyType + '.json', JSON.stringify(stories[storyType][year][month]));
        if ((year == new Date().getFullYear()) && (month == (new Date().getMonth() +1))) uploadFile(file, 'PLN_' + year + '_' + month + '_' + storyType + '.json', props.getProperty('POST_TO_PLN'));
        DriveApp.removeFile(file);
      }
    }
  }
  uploadFile(locFile, 'PLNLocations.json', props.getProperty('POST_TO_PLN'));
  uploadFile(locFile, 'PLNLocations.json', props.getProperty('POST_TO_NEWS'));
  DriveApp.removeFile(locFile);
}

function getFusionData(tableId) {
  var sql = 'SELECT * FROM ' + tableId;
  var data = FusionTables.Query.sqlGet(sql, { hdrs: false });
  return data.rows;
}

//////////////////////////////////////////////////////////////////////
// Function: uploadFile
// Inputs:
// - File: The file blob
// - Filename: The name the file should be saved as
// - PostTo: A location where the file upload can be posted to.
//////////////////////////////////////////////////////////////////////
function uploadFile(file, filename, postTo) {
  var boundary = 'librarieshacked';
  var blob = file.getBlob();
  var attributes = '{\"name\":\"' + filename + '\"}';
  
  var requestBody = Utilities.newBlob(
    "--"+boundary+"\r\n"
    + "Content-Disposition: form-data; name=\"attributes\"\r\n\r\n"
    + attributes+"\r\n"+"--"+boundary+"\r\n"
    + "Content-Disposition: form-data; name=\"file\"; filename=\""+blob.getName()+"\"\r\n"
    + "Content-Type: " + blob.getContentType()+"\r\n\r\n").getBytes()
    .concat(blob.getBytes())
    .concat(Utilities.newBlob("\r\n--"+boundary+"--\r\n").getBytes());
    
  var options = {
    method: "post",
    contentType: "multipart/form-data; boundary="+boundary,
    payload: requestBody,
    muteHttpExceptions: true
  };
  UrlFetchApp.fetch(postTo, options);
  return;
}