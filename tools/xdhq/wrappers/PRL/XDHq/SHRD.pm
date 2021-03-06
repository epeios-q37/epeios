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

package XDHq::SHRD;

use Config;

use constant {
    RT_VOID => 0,
    RT_STRING => 1,
    RT_STRINGS => 2
};

use constant {
    FALSE => undef,
    TRUE => not (undef)
};

sub isWin {
    return $Config{osname} eq "MSWin32";
}

sub isDev {
    return defined($ENV{"Q37_EPEIOS"});
}

sub isREPLit {
    return ( exists $ENV{"ATK"} ) && (uc($ENV{"ATK"}) eq "REPLIT");
}

sub open {
    my $os = $Config{osname};
    my $opener;

    if ( $os eq "MSWin32" ) {
        $opener = "start";
    } elsif ( $os eq "darwin" ) {
        $opener = "open"
    } elsif ( $os eq "cygwin" ) {
        $opener = "cygstart";
    } else {
        $opener = "xdg-open";
    }

    system($opener,shift);
}

return TRUE;

