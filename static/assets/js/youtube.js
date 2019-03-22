$('.js-youtube-vid').on('change', function(){

        var newval = '',
            $this = $(this);

        if (newval = $this.val().match(/(\?|&)v=([^&#]+)/)) {

            $this.val(newval.pop());

        } else if (newval = $this.val().match(/(\.be\/)+([^\/]+)/)) {

            $this.val(newval.pop());

        } else if (newval = $this.val().match(/(\embed\/)+([^\/]+)/)) {

            $this.val(newval.pop().replace('?rel=0',''));

        }

    });


var delay = (function() {
  var timer = 0;
  return function(callback, ms) {
    clearTimeout(timer);
    timer = setTimeout(callback, ms);
  };
})();

$('#youtubeId').keyup(function() {
  delay(function() {



    var videoID = $('#youtubeId').val();
    var videos = "https://www.googleapis.com/youtube/v3/videos";
    var apiKey = "AIzaSyAmvccE9BbsSqq4HNCJWKDJjx0FcGJRDuU"; // Insert here your api key
    var fieldsTitle = "fields=items(snippet(title))";
    var fieldsEmpty = "";
    var part = "part=snippet";

    function getUrl(fields) {
      var url = videos + "?" + "key=" + apiKey + "&" + "id=" + videoID + "&" + fields + "&" + part;
      return url;
    }

    $.get(getUrl(fieldsEmpty), function(response) {
      var status = response.pageInfo.totalResults;
      var title;
      if (status) {
        $.get(getUrl(fieldsTitle), function(response) {
          title = response.items[0].snippet.title;
          $('#info').text(title);
          var url = "https://www.youtube.com/embed/" + videoID;
          $('#myIframe').attr('src', url)
          $('#myIframe').attr('style', 'display: inline;')

          $('#youtube-video-embed').attr('value', url)
          $('#finished-video-embed').click(function() {
            var video = $('#videoframe').html();
            $('#video-area').html(video);

          })
        })
      } else {
        title = "Video doesn't exist or something messed up. Try again.";
        $('#info').text(title);
        
      }
    });
  }, 1000);
});


