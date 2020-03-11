=pod
MIT License

Copyright (c) 2019 Claude SIMON (https://q37.info/s/rmnmqd49)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
=cut

use strict; use warnings;

package XDHq::Faas;

use XDHq::SHRD;
use XDHq::Faas::SHRD;
use XDHq::Faas::Instance;
use IO::Socket::INET;
use threads;
use threads::shared;
use strict;

my $FaasProtocolLabel = "0fac593d-d65f-4cc1-84f5-3159c23c616b";
my $FaasProtocolVersion = "0";
my $mainProtocolLabel = "8d2b7b52-6681-48d6-8974-6e0127a4ca7e";
my $mainProtocolVersion = "0";

my $pAddr = "atlastk.org";
my $pPort = 53800;
my $wAddr = "";
my $wPort = "";
my $cgi = "xdh";

my $headContent: shared;
my $token = "";
my %instances;

sub trim { my $s = shift; $s =~ s/^\s+|\s+$//g; return $s };

sub getEnv {
    my ($name,$value) = @_;
    $value //= "";

    my $env= $ENV{$name};

    if (defined($env)) {
        return trim($env);
    } else {
        return return($value);
    }
}

sub _tokenIsEmpty {
    return ($token eq "") ||(substr($token,0,1) == "&");
}

sub _init {
    $token = "";
    my $atk = getEnv("ATK");

    if ($atk eq "" ) {}
    elsif ($atk eq "DEV") {
        $pAddr = "localhost";
        $wPort = "8080";
        CORE::say("\tDEV mode!");
    } elsif ($atk eq "TEST") {
        $cgi = "xdh_";
    } else  {
        die("Bad 'ATK' environment variable value : should be 'DEV' or 'TEST' !");
    }

    $pAddr = getEnv("ATK_PADDR", $pAddr);
    $pPort = getEnv("ATK_PPORT", "$pPort");
    $wAddr = getEnv("ATK_WADDR", $wAddr);
    $wPort = getEnv("ATK_WPORT", $wPort);

    if ($wAddr eq "") {
        $wAddr = $pAddr;
    }

    if ($wPort ne "") {
        $wPort = ":" . $wPort;
    }

    if (_tokenIsEmpty()) {
        $token = getEnv("ATK_TOKEN");
    }

    if ($token ne "") {
        $token = "&" . $token;
    }

    # auto-flush on socket
    $| = 1;

    # create a connecting socket
    $XDHq::Faas::SHRD::socket = new IO::Socket::INET (
        PeerHost => $pAddr,
        PeerPort => $pPort,
        Proto => 'tcp',
    );

    die("Error on connection to '${pAddr}:${pPort}': $! !!!\n") unless $XDHq::Faas::SHRD::socket;
}

sub _demoHandshake {
    XDHq::Faas::SHRD::writeString($FaasProtocolLabel);
    XDHq::Faas::SHRD::writeString($FaasProtocolVersion);

    my $error = XDHq::Faas::SHRD::getString();

    if ( $error ne "") {
        die($error);
    }

    my $notification = XDHq::Faas::SHRD::getString();

    if ( $notification ne "") {
        CORE::say($notification);
    }
}

sub _ignition {
    XDHq::Faas::SHRD::writeString($token);
    XDHq::Faas::SHRD::writeString($main::headContent);
    XDHq::Faas::SHRD::writeString($wAddr);

    $token = XDHq::Faas::SHRD::getString();

    if ( $token eq "") {
        die(XDHq::Faas::SHRD::getString());
    }

    if (not($wPort eq ":0")) {
#        my $url = "http://${wAddr}${wPort}/${cgi}.php?_token=${token}";
        my $url = XDHq::Faas::SHRD::getString();

        CORE::say($url);
        CORE::say("^" x length($url));
        CORE::say("Open above URL in a web browser. Enjoy!\n");
        XDHq::SHRD::open($url);
    }
}

sub _serve {
    my ($callback, $userCallback, $callbacks) = @_;

    while(XDHq::SHRD::TRUE) {
        my $id = XDHq::Faas::SHRD::getByte();

        if ( $id eq 255) {   # Value reporting a new front-end.
            $id = XDHq::Faas::SHRD::getByte();    # The id of the new front-end.

            if( $instances{$id} ) {
                die("Instance of id '${id}' exists but should not !")
            }

            my $instance : shared = XDHq::Faas::Instance::new();

            XDHq::Faas::Instance::set($instance, $callback->($userCallback, $callbacks, $instance),$id);

            $instances{$id}=$instance;

            {   # Locking scope.
                lock($XDHq::Faas::SHRD::writeLock);
                XDHq::Faas::SHRD::writeByte($id);
                XDHq::Faas::SHRD::writeString($mainProtocolLabel);
                XDHq::Faas::SHRD::writeString($mainProtocolVersion);
            }
        } elsif ( not($instances{$id})) {
            die("Unknown instance of id '${id}'!")
        } elsif (not(XDHq::Faas::Instance::testAndSetHandshake($instances{$id}))) {
            my $error = XDHq::Faas::SHRD::getString();

            if ($error) {
                die($error);
            }

            XDHq::Faas::SHRD::getString();    # Language. Not handled yet.

            {   # Lock scope;
                lock($XDHq::Faas::SHRD::writeLock);
                XDHq::Faas::SHRD::writeByte($id);
                XDHq::Faas::SHRD::writeString("PRL");
            }
        } else {
            XDHq::Faas::Instance::signal($instances{$id});

            lock($XDHq::Faas::SHRD::globalCondition);
            cond_wait($XDHq::Faas::SHRD::globalCondition);
        }
    }
}
        
sub launch {
    my ($callback, $userCallback, $callbacks, $headContent) = @_;

    $main::headContent = $headContent;

    _init();
    _demoHandshake();
    _ignition();
    _serve($callback, $userCallback, $callbacks);
}

return XDHq::SHRD::TRUE;