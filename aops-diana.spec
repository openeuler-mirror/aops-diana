Name:		aops-diana
Version:	v2.0.0
Release:	1
Summary:	An intelligent abnormal detection framework of aops
License:	MulanPSL2
URL:		https://gitee.com/openeuler/%{name}
Source0:	%{name}-%{version}.tar.gz


%description
An intelligent abnormal detection framework of aops

BuildRequires:  python3-setuptools
Requires:   aops-vulcanus = %{version}-%{release}
Requires:   python3-requests python3-flask python3-flask-restful python3-marshmallow >= 3.13.0
Requires:   python3-numpy python3-pandas python3-prometheus-api-client
Requires:   python3-sqlalchemy python3-PyMySQL python3-Flask-APScheduler >= 1.11.0
Requires:   python3-scipy
Provides:   aops-diana
Conflicts:  aops-check


%prep
%autosetup -n %{name}-%{version}


# build for aops-diana
%py3_build


# install for aops-diana
%py3_install


%files
%doc README.*
%attr(0644,root,root) %{_sysconfdir}/aops/diana.ini
%attr(0644,root,root) %{_sysconfdir}/aops/diana_default.json
%attr(0755,root,root) %{_bindir}/aops-diana
%attr(0755,root,root) %{_unitdir}/aops-diana.service
%{python3_sitelib}/diana*.egg-info
%{python3_sitelib}/diana/*


%changelog
* Sun Oct 9 2022 zhuyuncheng<zhuyuncheng@huawei.com> - v2.0.0-1
- Package init
