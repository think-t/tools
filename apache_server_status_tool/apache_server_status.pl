#!/usr/bin/perl
# Author  : think-t
# Blog    : http://think-t.hatenablog.com

use warnings;
use strict;
use LWP::UserAgent;
use Fcntl;

my $hostname = "127.0.0.1";             # Name of server
my $port     = "80";                    # Port on server
my $address  = "server-status/?auto";   # Server Status Address
my $log_directory = "/var/log";         # Log Directory

my $url = "http://$hostname:$port/$address";

my ( $year, $month, $month_of_day, $hour, $minute ) = &get_current_time ( );
my $yyyyMMdd = sprintf ( "%04d%02d%02d", $year, $month, $month_of_day );
my $log_file = "$log_directory/$yyyyMMdd.server-status.log";

my %server_status = (
    'total_access' => '',
    'total_kbytes' => '',
    'uptime' => '',
    'req_per_sec' => '',
    'bytes_per_sec' => '',
    'bytes_per_req' => '',
    'busyworkers' => '',
    'idleworkers' => '',
    'scoreboard' => '',
);

my %scoreboard_count = (
    '_' => 0,        # Waiting for Connection
    'S' => 0,        # Starting up
    'R' => 0,        # Reading Request
    'W' => 0,        # Sending Reply
    'K' => 0,        # Keepalive(read)
    'D' => 0,        # DNS Lookup
    'C' => 0,        # Closing connection
    'L' => 0,        # Logging
    'G' => 0,        # Gracefully finishing
    'I' => 0,        # Idle cleanup of worker
    '.' => 0,        # Open slot with no current process
);

my $response = &get_server_status ( );

if ( $response -> is_success ){
    my $response_data = $response -> content;
    %server_status = &pick_out_server_status_value ( $response_data, \%server_status );

    %scoreboard_count = &count_scoreboard_count ( $server_status{'scoreboard'}, \%scoreboard_count );

    my $message = &collect_server_status_value ( \%server_status, \%scoreboard_count );

    &write_log ( $log_file, $message ); 
} else {
    my $date = sprintf ( "%04d/%02d/%02d", $year, $month, $month_of_day );
    my $time = sprintf ( "%02d:%02d", $hour, $minute );
    my $message = "$date,$time,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0";

    &write_log ( $log_file, $message );
}

sub get_current_time {
    my ( $second, $minute, $hour, $month_of_day, $month, $year ) = localtime ( );
    $year += 1900;
    $month++;

    return ( $year, $month, $month_of_day, $hour, $minute );
}

sub get_server_status {
    my $agent = LWP::UserAgent -> new;
    my $request = HTTP::Request -> new ( GET => $url );
    my $response = $agent -> request ( $request );
    
    return $response;
}

sub pick_out_server_status_value {
    my ( $response_data, $server_status ) = @_;

    if ( $response_data =~ m|^Total\ Accesses:\ (\S+)|m ) { $server_status{'total_access'} = $1 }; 
    if ( $response_data =~ m|^Total\ kBytes:\ (\S+)|m ) { $server_status{'total_kbytes'} = $1 }; 
    if ( $response_data =~ m|^Uptime:\ (\S+)|m ) { $server_status{'uptime'} = $1 };
    if ( $response_data =~ m|^ReqPerSec:\ (\S+)|m ) { $server_status{'req_per_sec'} = $1 };
    if ( $response_data =~ m|^BytesPerSec:\ (\S+)|m ) { $server_status{'bytes_per_sec'} = $1 };
    if ( $response_data =~ m|^BytesPerReq:\ (\S+)|m ) { $server_status{'bytes_per_req'} = $1 };
    if ( $response_data =~ m|^BusyWorkers:\ (\S+)|m ) { $server_status{'busyworkers'} = $1 };
    if ( $response_data =~ m|^IdleWorkers:\ (\S+)|m ) { $server_status{'idleworkers'} = $1 };
    if ( $response_data =~ m|^Scoreboard:\ (\S+)|m ) { $server_status{'scoreboard'} = $1 };

    return %server_status;
}

sub count_scoreboard_count {
    my ( $scoreboard, $scoreboard_count ) = @_;

    $scoreboard_count{'_'} = $scoreboard =~ tr/_/_/;
    $scoreboard_count{'S'} = $scoreboard =~ tr/S/S/;
    $scoreboard_count{'R'} = $scoreboard =~ tr/R/R/;
    $scoreboard_count{'W'} = $scoreboard =~ tr/W/W/;
    $scoreboard_count{'K'} = $scoreboard =~ tr/K/K/;
    $scoreboard_count{'D'} = $scoreboard =~ tr/D/D/;
    $scoreboard_count{'C'} = $scoreboard =~ tr/C/C/;
    $scoreboard_count{'L'} = $scoreboard =~ tr/L/L/;
    $scoreboard_count{'G'} = $scoreboard =~ tr/G/G/;
    $scoreboard_count{'I'} = $scoreboard =~ tr/I/I/;
    $scoreboard_count{'.'} = $scoreboard =~ tr/././;

    return %scoreboard_count;
}

sub collect_server_status_value {
    my ( $server_status, $scoreboard_count ) = @_;
    my ( $year, $month, $month_of_day, $hour, $minute ) = &get_current_time ( );

    my $date = sprintf ( "%04d/%02d/%02d", $year, $month, $month_of_day );
    my $time = sprintf ( "%02d:%02d", $hour, $minute );
    my $message = "$date,$time,$server_status{'total_access'},$server_status{'total_kbytes'},$server_status{'uptime'},"
                  . "$server_status{'req_per_sec'},$server_status{'bytes_per_sec'},$server_status{'bytes_per_req'},"
                  . "$server_status{'busyworkers'},$server_status{'idleworkers'},"
                  . "$scoreboard_count{'_'},$scoreboard_count{'S'},$scoreboard_count{'R'},$scoreboard_count{'W'},"
                  . "$scoreboard_count{'K'},$scoreboard_count{'D'},$scoreboard_count{'C'},$scoreboard_count{'L'},"
                  . "$scoreboard_count{'G'},$scoreboard_count{'I'},$scoreboard_count{'.'}";

    return $message;
}

sub write_log {
    my ( $log_file, $message ) = @_;

    my $header = "date,time,total_access,total_kbytes,uptime,"
                 . "req_per_sec,bytes_per_sec,bytes_per_req,busyservers,idleservers,"
                 . "waiting,starting_up,reading,sending,reading_keepalive,"
                 . "look_up_dns,closing,logging,finishing_gracefully,clean_up_idle,open_slot";

    if ( -f $log_file ){
        sysopen ( my $fh, $log_file, O_WRONLY|O_APPEND|O_CREAT ) or die $!;
        print $fh $message . "\n";
        close ( $fh );
    } else { 
        sysopen ( my $fh, $log_file, O_WRONLY|O_APPEND|O_CREAT ) or die $!;
        print $fh $header . "\n";
        print $fh $message . "\n";
        close ( $fh );
    }
}

exit 0;
