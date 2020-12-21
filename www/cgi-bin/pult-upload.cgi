#!/usr/bin/perl -w

use strict;
use File::Basename;
use CGI;
use CGI::Carp qw ( fatalsToBrowser );
use Time::HiRes qw ( usleep );

my ( $name, $path, $ext ) = fileparse ( $0, '-[1-6]\.cgi' );
my $channel = substr ( $ext, 1, 1 );
my $ws_number = 20 + $channel;

my $config_file = "/usr/local/var/run/pult/upload-$channel.pl";

$CGI::POST_MAX = 8 * 1024 * 1024;
my $pultd_port = 6070 + $channel;
my $module_name = $name;
my $msg_not_running = "<p>This page is currently closed.</p>\n";
my $upload_dir = "/usr/local/var/spool/pult";
my $web_dir = "/var/www/streaming";
my $download_dir = "/pult-upload";
my $filename = "pult-uploaded-" . $channel . ".tmp";
my $pointer_filename = "pult/pointer.png";
my $lock_filename = "pult-uploaded-" . $channel . ".lock";
my $error_filename = "pult-uploaded-" . $channel . ".err";

my $query = new CGI;
my $cmd = $query->param ( "cmd" ) || "";
my $upload_done = $cmd ? $cmd eq "show-image" : 0;
my $daemon_running = 0;

if ( open CONFIG, "$config_file" )
  {
    my $config = join "", <CONFIG>;
    close CONFIG;
    eval $config;
    if ( $@ )
      {
        die "could not read configuration from \"$config_file\": $@\n";
      }
    $daemon_running = 1;

    my $upload_filehandle = $query->upload ( "image_file" );

    if ( $channel >= 1 && $channel <= 6 && $upload_filehandle )
      {
        system ( "echo $module_name reset | nc localhost $pultd_port >/dev/null" );
        usleep ( 1000000 );
        open ( UPLOADFILE, ">$upload_dir/$filename" ) or die "$!";
        binmode UPLOADFILE;
        while ( <$upload_filehandle> )
          {
            print UPLOADFILE;
          }
        close UPLOADFILE;
        system ("chmod 464 $upload_dir/$filename");
      }
  }

print $query->header ( );

print <<EOF;
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "DTD/xhtml1-strict.dtd"> 
<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf8">
    <title>PULT Upload</title>
    <link rel="stylesheet" href="/pult/stylesheets/default.css" type="text/css">
  </head>
  <body>
EOF

if ( ! $daemon_running )
  {
    print "    $msg_not_running";
  }
elsif ( $upload_done )
  {
    system ( "echo $module_name $cmd | nc localhost $pultd_port >/dev/null" );
    while ( -f "$config_file" && ( -f "$upload_dir/$filename" || -f "$upload_dir/$lock_filename" ) )
      {
        usleep ( 10000 );
      }
    usleep ( 10000 );
    if ( -f "$upload_dir/$error_filename" )
      {
        my $error_message;
        open ( ERROR_FILE, '<', "$upload_dir/$error_filename" ) or $error_message = "unknown error";
        $error_message = <ERROR_FILE>;
        print <<EOF;
    <form action="/cgi-bin/pult-upload-$channel.cgi" method="post" enctype="multipart/form-data">
      <button type="submit" class="upload">Reset</button>
      <input type="hidden" name="cmd" value="reset" />
    </form>
    <p>$error_message</p>
EOF
      }
    else
      {
        print <<EOF;
    <form action="/cgi-bin/pult-upload-$channel.cgi" method="post" enctype="multipart/form-data">
      <button type="submit" class="upload">Reset</button>
      <input type="hidden" name="cmd" value="reset" />
    </form>
    <p id="image_container" style="position: relative;">
      <img style="position: absolute; left: 0px; top: 0px; z-index: 0;"
           src="$download_dir/$filename" alt="uploaded image" />
      <img id="pointer"
           style="display: none; position: absolute; left: 0px; top: 0px; z-index: 1;"
           src="$web_dir/$pointer_filename" alt="pointer" />
    </p>
    <script>

      parent = document.getElementById ("image_container");
      pointer = document.getElementById ("pointer");

      socket = new WebSocket ("wss://streaming.cvh-server.de/websock/$ws_number/", ['binary', 'base64']);
      socket_ready = false;

      socket.addEventListener ("open", async function (event) {
        socket_ready = true;
        console.log ("WebSocket opened ", event.data);
      });

      socket.addEventListener ("close", async function (event) {
        socket_ready = false;
        console.log ("WebSocket closed: ", event.data);
      });

      socket.addEventListener ("message", async function (event) {
        console.log ("WebSocket data: ", event.data);
      });

      socket.addEventListener ("error", async function (event) {
        console.log ("WebSocket error: ", event.data);
      });

      document.addEventListener ("click", async function (evt) {
        x = event.clientX - parent.offsetLeft;
        y = event.clientY - parent.offsetTop;

        var xOffset = (window.pageXOffset !== undefined)
          ? window.pageXOffset
          : (document.documentElement || document.body.parentNode || document.body).scrollLeft;
        var yOffset = (window.pageYOffset !== undefined)
          ? window.pageYOffset
          : (document.documentElement || document.body.parentNode || document.body).scrollTop;
        // console.log ("Offsets ", xOffset, " ", yOffset);
        x += Math.trunc (xOffset);
        y += Math.trunc (yOffset);

        pointer.style.display = "inherit";
        pointer.style.left = `\${x - 2}px`;
        pointer.style.top = `\${y - 2}px`;
        if (socket_ready)
          {
            console.log ("Sending to WebSocket: pointer ", x, " ", y);
            await socket.send (`pointer \${x} \${y}\n`);
          }
        else
          console.log ("WebSocket is not ready while trying to send: pointer ", x, " ", y);
      }, false);

    </script>
EOF
      }
  }
else
  {
    if ( $cmd eq "reset" )
      {
        system ( "echo $module_name $cmd | nc localhost $pultd_port >/dev/null" );
      }

    print <<EOF;
    <form name="upload_form" action="/cgi-bin/pult-upload-$channel.cgi" method="post" enctype="multipart/form-data">
      <input type="file" class="upload" name="image_file" value="Datei auswählen"/>
      <button type="submit" class="upload" name="submit">Bilddatei hochladen</button>
      <input type="hidden" id="cmd" name="cmd" value="show-image"/>
      &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
      <button type="button" id="screenshot" class="upload">Screenshot hochladen</button>
    </form>
    <video id="video" style="display: none;" autoplay></video>
    <canvas id="canvas" style="display: none;"></canvas>
    <p id="progress_bar_container" style="display: none; width: 80%; border: solid 1pt">
      <span id="progress_bar" style="padding-left: 1%; background-color: #e2001a;">&#8203;</span>
    </p>
    <script>

      const video = document.getElementById ("video");
      const canvas = document.getElementById ("canvas");

      var displayMediaOptions = {
        video: { cursor: "always" },
        audio: false
      };

      async function startCapture () {
        video.srcObject = await navigator.mediaDevices.getDisplayMedia (displayMediaOptions);
      }

      function stopCapture (evt) {
        let tracks = video.srcObject.getTracks ();
        tracks.forEach (track => track.stop ());
        video.srcObject = null;
      }

      document.getElementById ("screenshot").addEventListener ("click",
        function (evt) {
          startCapture ();
        }, false);

      const sleep = (delay) => new Promise ((resolve) => setTimeout (resolve, delay));

      function sendData (data, w, h) {
        const chunk_size = 1024;
        var total_size = data.length;
        console.log ("Opening WebSocket ...");
        var socket = new WebSocket ("wss://streaming.cvh-server.de/websock/$ws_number/", ['binary', 'base64']);
        socket.addEventListener ("open", async function (event) {
          socket.send ("screenshot " + (w).toString () + " " + (h).toString () + "\\n");
          console.log ("Sending data ...");
          while (data.length > 0)
            {
              if (socket.bufferedAmount > 0)
                {
                  var written_size = total_size - data.length;
                  var percentage = written_size * 100 / total_size;
                  document.getElementById ("progress_bar").style.paddingLeft = (percentage).toString () + "%";
                  document.getElementById ("progress_bar_container").style.display = "inherit";
                  await sleep (10);
                }
              else if (data.length > chunk_size)
                {
                  socket.send (data.substring (0, chunk_size) + "\\n");
                  data = data.substring (chunk_size);
                }
              else
                {
                  socket.send (data + "\\n");
                  data = "";
                }
            }
          socket.send ("\\n");
          await sleep (100);  // Why is this necessary? Doesn't the WebSocket flush on close()?
          socket.close ();
        });
        socket.addEventListener ("close", async function (event) {
          console.log ("... done.");
          document.getElementById ("progress_bar_container").style.display = "none";
          // document.getElementById ("cmd").value = "show-screenshot";
          document.upload_form.submit.click ();
          // window.location.href = "pult-upload-show-$channel?cmd=show-screenshot";
        });
      }

      document.addEventListener ("DOMContentLoaded", () => {
        video.addEventListener ("play",
          function () {
            w = video.videoWidth;
            h = video.videoHeight;
            canvas.width = w;
            canvas.height = h;
            ctx = canvas.getContext ("2d");
            ctx.drawImage (video, 0, 0, w, h);
            stopCapture ();
            var uri = canvas.toDataURL('image/jpeg'),
            data = uri.replace(/^data:image.+;base64,/, '');
            sendData (data, w, h);
          }, false);
      });

    </script>
EOF
  }

print <<EOF;
  </body> 
</html> 
EOF
