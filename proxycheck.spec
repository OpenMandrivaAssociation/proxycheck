%define name	proxycheck
%define version	0.49a
%define release	%mkrel 7

Name:		%{name}
Version:	%{version}
Release:	%{release}
Summary:	A quick open proxy scanner
Epoch:		1
License:	GPL
Group:		Networking/Other
URL:		http://www.corpit.ru/mjt/proxycheck.html
Source0		http://www.corpit.ru/mjt/proxycheck/%{name}-%{version}.tar.bz2
Source1:	%{name}.logrotate.bz2
Requires(pre):	rpm-helper
BuildRoot:	%{_tmppath}/%{name}-%{version}

%description
Proxycheck is a simple tool to quickly check whenever a given host or set of
hosts has open proxy server running. Open proxies of various kinds are (ab)used
nowadays for various evil things like sending mass spam, hacking into your
machine, making denial of service attacks (DoS) and the like. To stop the abuse
of open proxy servers, one need to know whenever any machine runs such service
or not.
This command-line tool, proxycheck, may be used for such purpose. Currently, it
understands 3 types of proxy servers: HTTP proxies that allows you to CONNECT
to any host:port, SOCKS v4 and v5 proxies (www.socks.nec.com), and wingate
"telnet" proxy servers.

%package proxylogger
Summary:	Receiving part of proxycheck
Group:		Networking/Other
Requires:	xinetd
Requires(post,preun):	rpm-helper

%description proxylogger
Proxylogger is a trivial program (invoked from xinetd) that writes out a string
"550 ESMTP_unwelcome [peer.ip.add.ress]" to the network and optionally waits
for a string in form
    [junk]protocol:ip.add.re.ss:port\n
from the remote system.  May be used as a destination for proxycheck program.
All connections (together with the information in the above form, if given) are
optionally logged to a specified file.

To use proxylogger from proxycheck, use a command like:
  proxycheck -c chat::ESMTP_unwelcome -d your.ip.add.ress:25 host-to-be-checked

%prep
%setup -q
bzcat %{SOURCE1} > %{name}.logrotate

%build
./configure
%make CFLAGS="%{optflags}" proxycheck proxylogger

%install
rm -rf %{buildroot}

# Makefile lacks install fase
install -d -m 755 %{buildroot}%{_bindir}
install -d -m 755 %{buildroot}%{_mandir}/man1
install -m 755 %{name} proxylogger %{buildroot}%{_bindir}
install -m 644 %{name}.1 %{buildroot}%{_mandir}/man1

install -d -m 755 %{buildroot}%{_sysconfdir}/xinetd.d
cat <<EOF > %{buildroot}%{_sysconfdir}/xinetd.d/proxylogger
# default: off
# description: Proxylogger is the receiving part of proxycheck, \
# to be used from (x)inetd and with -c chat
#

service smtp
{
    disable             = yes
    socket_type         = stream
    wait                = no
    protocol            = tcp
    user                = proxylogger
    group               = proxylogger
    server              = %{_bindir}/proxylogger
    server_args         = -l /var/log/proxylogger/info
}

EOF
install -d -m 755 %{buildroot}%{_var}/log/%{name}

install -d -m 755 %{buildroot}%{_sysconfdir}/logrotate.d
install -m 644 %{name}.logrotate %{buildroot}%{_sysconfdir}/logrotate.d/%{name}

%clean
rm -rf %{buildroot}

%pre proxylogger
%_pre_useradd proxylogger /var/log/proxylogger /bin/false

%postun proxylogger
%_postun_userdel proxylogger

%files
%defattr(-,root,root)
%doc CHANGES
%{_bindir}/%{name}
%{_mandir}/man1/%{name}.1*

%files proxylogger
%defattr(-,root,root)
%{_bindir}/proxylogger
%config(noreplace) %_sysconfdir/xinetd.d/proxylogger
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%attr(-,proxylogger,proxylogger) %{_var}/log/%{name}

