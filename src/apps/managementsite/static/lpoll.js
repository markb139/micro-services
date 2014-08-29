var prev_data = null,           // remember data fetched last time
    waiting_for_update = false, // are we currently waiting?
    LONG_POLL_DURATION = 60000; // how long should we wait? (msec)

function load_data() {
    var url = '/data'

    $.ajax({ url:     url,
             success: function(data) {
                          display_data(data);
                          wait_for_update();
                      }
    });
    return true;
}

function wait_for_update() {
    // Uses separate update notification and data providing URLs. Could be
    // combined, but if they're separated, the Python routine that provides
    // data needn't be changed from what's required for standard, non-long-polling
    // web app. If they're combined, arguably over-loads the purpose of the function.

    if (!waiting_for_update) {
        waiting_for_update = true;
        $.ajax({ url: '/updated',
                 success: function(data) {
                   if (data == 'changed') {
                       load_data();
                   }
                 },
                 complete: function () {
                    waiting_for_update = false;
                    wait_for_update(); // if the wait_for_update poll times out, rerun
                 },
                 timeout:  LONG_POLL_DURATION
               });
    }

    // wait_for_update guard to ensure not re-entering already running wait code
    // added after user suggestion. This check has not been needed in my apps
    // and testing, but concurrency is an area where an abundance of caution is
    // often the best policy.
}

function display_data(data) {
    // show the data acquired by load_data()

    if (data && (data != prev_data)) {      // if there is data, and it's changed

        // update the contents of several HTML divs via jQuery
        // $('div#contents').html(data.contents);
        var template = $('#valueTpl').html();
        var html = Mustache.to_html(template, data);
        $('div#contents').html(html);

        // remember this data, in case want to compare it to next update
        prev_data = data;

        // a little UI sparkle - show the #updated div, then after a little
        // while, fade it away
        $("#updated").fadeIn('fast');
        setTimeout(function() {  $("#updated").fadeOut('slow');  }, 2500);
    }
}

function buttonclicked(id) {
    var sel = "textarea#tx-" + id
    var route = id + "." + $(sel).val()
    sel = "textarea#msg-" + id
    var body = $(sel).val()
    var sendData = {key: route, body: body};

    $.ajax({
        url: '/send',
        type: 'POST',
        data : JSON.stringify(sendData, null, '\t'),
        contentType: 'application/json;charset=UTF-8',
        error: function(data){
            alert(data);
        }
    });
}

$(document).ready(function() {
    $("div#updated").fadeOut(0);
    $("div#contents").append("awaiting data...");

    // load the initial data (assuming it will be immediately available)
    load_data();
});
