%define debug_package %{nil}
%define base_install_dir %{_javadir}{%name}

Name: elasticsearch
Version: 0.90.9
Release: 1
Summary: A distributed, highly available, RESTful search engine

Group: System Environment/Daemons
License: ASL 2.0
URL: http://www.elasticsearch.com
Source0: https://download.elasticsearch.org/%{name}/%{name}/%{name}-%{version}.tar.gz
Source1: init.d-elasticsearch
Source2: logrotate.d-elasticsearch
Source3: config-logging.yml
Source4: sysconfig-elasticsearch
Source5: monitoring.yaml
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Requires: jpackage-utils
Requires: jre
Requires: %{name}-config
Requires: nc

Requires(post): chkconfig initscripts
Requires(pre): chkconfig initscripts
Requires(pre): shadow-utils

%description
A distributed, highly available, RESTful search engine

%prep
%setup -q -n %{name}-%{version}

%build
true

%install
rm -rf $RPM_BUILD_ROOT

%{__mkdir} -p %{buildroot}%{_javadir}/%{name}/bin
%{__install} -p -m 755 bin/elasticsearch %{buildroot}%{_javadir}/%{name}/bin
%{__install} -p -m 644 bin/elasticsearch.in.sh %{buildroot}%{_javadir}/%{name}/bin
%{__install} -p -m 755 bin/plugin %{buildroot}%{_javadir}/%{name}/bin

#libs
%{__mkdir} -p %{buildroot}%{_javadir}/%{name}/lib/sigar
%{__install} -p -m 644 lib/*.jar %{buildroot}%{_javadir}/%{name}/lib
%{__install} -p -m 644 lib/sigar/*.jar %{buildroot}%{_javadir}/%{name}/lib/sigar
%ifarch i386
%{__install} -p -m 644 lib/sigar/libsigar-x86-linux.so %{buildroot}%{_javadir}/%{name}/lib/sigar
%endif
%ifarch x86_64
%{__install} -p -m 644 lib/sigar/libsigar-amd64-linux.so %{buildroot}%{_javadir}/%{name}/lib/sigar
%endif

# config
%{__mkdir} -p %{buildroot}%{_sysconfdir}/elasticsearch
%{__install} -m 644 config/elasticsearch.yml %{buildroot}%{_sysconfdir}/%{name}
%{__install} -m 644 %{SOURCE3} %{buildroot}%{_sysconfdir}/%{name}/logging.yml

# monitoring
%{__mkdir} -p %{buildroot}%{_sysconfdir}/monitoring
%{__install} -m 644 %{SOURCE5} %{buildroot}%{_sysconfdir}/monitoring/20_elasticsearch.yaml

# data
%{__mkdir} -p %{buildroot}%{_localstatedir}/lib/%{name}

# logs
%{__mkdir} -p %{buildroot}%{_localstatedir}/log/%{name}
%{__install} -D -m 644 %{SOURCE2} %{buildroot}%{_sysconfdir}/logrotate.d/elasticsearch

# plugins
%{__mkdir} -p %{buildroot}%{_javadir}/%{name}/plugins

# sysconfig and init
%{__mkdir} -p %{buildroot}%{_sysconfdir}/rc.d/init.d
%{__mkdir} -p %{buildroot}%{_sysconfdir}/sysconfig
%{__install} -m 755 %{SOURCE1} %{buildroot}%{_sysconfdir}/rc.d/init.d/elasticsearch
%{__install} -m 755 %{SOURCE4} %{buildroot}%{_sysconfdir}/sysconfig/elasticsearch

%{__mkdir} -p %{buildroot}%{_localstatedir}/run/elasticsearch
%{__mkdir} -p %{buildroot}%{_localstatedir}/lock/subsys/elasticsearch

%pre
# create elasticsearch group
if ! getent group elasticsearch >/dev/null; then
        groupadd -r elasticsearch
fi

# create elasticsearch user
if ! getent passwd elasticsearch >/dev/null; then
        useradd -r -g elasticsearch -d %{_javadir}/%{name} \
            -s /sbin/nologin -c "You know, for search" elasticsearch
fi

%post
/sbin/chkconfig --add elasticsearch
/sbin/chkconfig elasticsearch on
# always restart elasticsearch if it was running
if service elasticsearch status > /dev/null 2>&1; then
        echo "Restarting elasticsearch service because it was running."
        if ! service elasticsearch restart ; then
                logger -p user.err -s -t "%{name}" -- "ERROR: Installation failure. Not able to restart the service." 
                exit 0
        fi
fi


%preun
if [ $1 -eq 0 ]; then
  /sbin/service elasticsearch stop >/dev/null 2>&1
  /sbin/chkconfig --del elasticsearch
fi

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%{_sysconfdir}/rc.d/init.d/elasticsearch
%dir %{_javadir}/elasticsearch
%{_javadir}/elasticsearch/bin/*
%{_javadir}/elasticsearch/lib/*
%dir %{_javadir}/elasticsearch/plugins
%doc LICENSE.txt NOTICE.txt README.textile
%defattr(-,elasticsearch,elasticsearch,-)
%dir %{_localstatedir}/lib/elasticsearch
%{_localstatedir}/run/elasticsearch


%package -n %{name}-default-config

Requires: yum
Provides: %{name}-config
Summary: Default config files for %{name}

%description -n %{name}-default-config

This package contains the default configuration for %{name}. Other providers of %{name}-config could deliver
server or environment specific configuration files.

%files -n %{name}-default-config
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/sysconfig/elasticsearch
%config(noreplace) %{_sysconfdir}/monitoring/20_elasticsearch.yaml
%{_sysconfdir}/logrotate.d/elasticsearch
%config(noreplace) %{_sysconfdir}/elasticsearch
%dir %{_localstatedir}/log/elasticsearch

%changelog
* Wed Oct 02 2013 jgaedicke 0.90.5-7
- update to elasticsearch 0.90.5
- added default monitoring for is24

* Thu Sep 12 2013 jgaedicke 0.20.6-6
- start elasticsearch service on reboot
- sleep 2 seconds when restarting service, to free used system memory

* Fri Jun 14 2013 jgaedicke 0.20.6-3
- restart elasticsearch if service was running

* Fri Jun 14 2013 jgaedicke 0.20.6-1
- update to 0.20.6 and check cluster health in init script

* Mon Dec 10 2012 tavisto@tavisto.net 0.20.1-1
- Changed the dependancy of java to jre to be more compatible with Sun Java

* Mon Dec 10 2012 tavisto@tavisto.net 0.20.1-1
- New upstream version

* Tue Nov 27 2012 tavisto@tavisto.net 0.19.11-1
- New upstream version

* Sun Mar 11 2012 tavisto@tavisto.net 0.19.0-1
- New Upstream version, as well as splitting out the plugins into their own rpms

* Tue Jan 10 2012 Tavis Aitken <tavisto@tavisto.net> - 0.18.7-1
- New Upstream version

* Thu Dec 28 2011 Tavis Aitken <tavisto@tavisto.net> - 0.18.6-1
- New upstream version

* Thu Dec 01 2011 Tavis Aitken <tavisto@tavisto.net> - 0.18.5-1
- New upstream version

* Sat Nov 26 2011 Tavis Aitken <tavisto@tavisto.net> - 0.18.4-1
- New upstream version

* Mon Oct 31 2011 Dan Carley <dan.carley@gmail.com> - 0.18.2-2
- Raise open files limit.

* Sat Oct 29 2011 Tavis Aitken <tavisto@tavisto.net> - 0.18.2-1
- New upstream version.

* Mon Jul 25 2011 Erick Tryzelaar erick.tryzelaar@gmail.com 0.17.1-1
- New Upstream version

* Thu Jul 14 2011 Erick Tryzelaar erick.tryzelaar@gmail.com 0.16.4-1
- New Upstream version
- Add analysis-icu, cloud-aws, hadoop, lang-groovy, lang-python,
  mapper-attachments, transport-memcached, transport-thrift, and
  transports-wares plugin subpackages

* Fri Jun 24 2011 Dan Everton dan.everton@wotifgroup.com 0.16.2-2
- Set plugins path so they are automatically detected by ES.

* Thu Jun 02 2011 Dan Everton dan.everton@wotifgroup.com 0.16.2-1
- New Upstream version

* Wed May 11 2011 Tavis Aitken tavisto@tavisto.net 0.16.0-2
- Add lang-javascript plugin subpackage

* Thu Apr 28 2011 Tavis Aitken tavisto@tavisto.net 0.16.0-1
- New upstream version

* Wed Apr 06 2011 Dan Carley <dan.carley@gmail.com> 0.15.2-2
- Moved data to /var/lib
- Allow customisation of paths.
- Allow customisation of memory and include settings.

* Mon Mar 07 2011 Tavis Aitken tavisto@tavisto.net 0.15.2-1
- New Upstream version

* Mon Mar 07 2011 Tavis Aitken tavisto@tavisto.net 0.15.1-1
- New Upstream version

* Mon Mar 01 2011 Tavis Aitken tavisto@tavisto.net 0.15.0-1
- New Upstream version

* Mon Feb 28 2011 Tavis Aitken tavisto@tavisto.net 0.14.3-0
- New Upstream version

* Sat Jan 29 2011 Tavis Aitken tavisto@tavisto.net 0.14.3-2
- Fixed the paths for the plugin sub-packages

* Sat Jan 29 2011 Tavis Aitken tavisto@tavisto.net 0.14.3-1
- Update to upstream version, complete with river plugin sub-packages

* Sat Jan 29 2011 Tavis Aitken tavisto@tavisto.net 0.14.2-3
- Fixed the user creation comment to not include a colon

* Fri Jan 21 2011 Tavis Aitken <tavisto@tavisto.net> - 0.14.2-2
- Fixed the logging.yml and logrotate.d configs

* Fri Jan 14 2011 Tavis Aitken <tavisto@tavisto.net> - 0.14.2-1
- New upstream version, and added specific arch suport for the sigar libraries.

* Tue Jan 4 2011 Tavis Aitken <tavisto@tavisto.net> - 0.14.1-1
- Initial package
