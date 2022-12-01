Name:		aops-diana
Version:	v1.1.0
Release:	1
Summary:	An intelligent abnormal detection framework of aops
License:	MulanPSL2
URL:		https://gitee.com/openeuler/%{name}
Source0:	%{name}-%{version}.tar.gz

BuildRequires:  python3-setuptools
Requires:   aops-vulcanus >= v1.0.0
Requires:   python3-requests python3-flask python3-flask-restful python3-marshmallow >= 3.13.0
Requires:   python3-numpy python3-pandas python3-prometheus-api-client
Requires:   python3-sqlalchemy python3-PyMySQL python3-Flask-APScheduler >= 1.11.0
Requires:   python3-scipy python3-adtk
Provides:   aops-diana
Conflicts:  aops-check


%description
An intelligent abnormal detection framework of aops


%prep
%autosetup -n %{name}-%{version}


# build for aops-diana
%py3_build


# install for aops-diana
%py3_install


%files
%doc README.*
%attr(0644,root,root) %{_sysconfdir}/aops/diana.ini
%attr(0644,root,root) %{_sysconfdir}/aops/diana_hosts.json
%attr(0644,root,root) %{_sysconfdir}/aops/algorithm/ai_template1.json
%attr(0644,root,root) %{_sysconfdir}/aops/algorithm/ai_template2.json
%attr(0644,root,root) %{_sysconfdir}/aops/algorithm/mysql_intelligent.json
%attr(0644,root,root) %{_sysconfdir}/aops/algorithm/lvs_network_error_tree.json
%attr(0644,root,root) %{_sysconfdir}/aops/algorithm/mysql_network_error_tree.json
%attr(0644,root,root) %{_sysconfdir}/aops/algorithm/tpcc_network_error_tree.json
%attr(0755,root,root) %{_bindir}/aops-diana
%attr(0755,root,root) /usr/lib/systemd/system/aops-diana.service
%{python3_sitelib}/aops_diana*.egg-info
%{python3_sitelib}/diana/*


%changelog
* Fri Dec 2 2022 zhuyuncheng<zhuyuncheng@huawei.com> - v1.1.0-1
- Update multi-item check algorithm

* Tue Nov 22 2022 zhuyuncheng<zhuyuncheng@huawei.com> - v1.0.0-1
- Package init
