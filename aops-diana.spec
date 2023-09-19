Name:		aops-diana
Version:	v1.3.0
Release:	1
Summary:	An intelligent abnormal detection framework of aops
License:	MulanPSL2
URL:		https://gitee.com/openeuler/%{name}
Source0:	%{name}-%{version}.tar.gz

BuildRequires:  python3-setuptools
Requires:   aops-vulcanus >= v1.2.0
Requires:   python3-requests python3-flask python3-flask-restful python3-marshmallow >= 3.13.0
Requires:   python3-numpy python3-pandas python3-prometheus-api-client python3-uWSGI
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
mkdir -p %{buildroot}/opt/aops/
cp -r database %{buildroot}/opt/aops/


%files
%doc README.*
%attr(0644,root,root) %{_sysconfdir}/aops/diana.ini
%attr(0644,root,root) %{_sysconfdir}/aops/diana_hosts.json
%attr(0644,root,root) %{_sysconfdir}/aops/algorithm/*.json
%attr(0644,root,root) %{_sysconfdir}/aops/algorithm/intelligent/*
%attr(0755,root,root) %{_bindir}/aops-diana
%attr(0755,root,root) /usr/lib/systemd/system/aops-diana.service
%{python3_sitelib}/aops_diana*.egg-info
%{python3_sitelib}/diana/*
%attr(0755, root, root) /opt/aops/database/*


%changelog
* Mon Sep 18 2023 gongzhengtang<gong_zhengtang@163.com> - v1.3.0-1
- Support sql script to create tables

* Fri Mar 24 2023 gongzhengtang<gong_zhengtang@163.com> - v1.2.0-1
- update the structure of response body; update how to get session used to
- connect to the database

* Mon Dec 19 2022 wangguangge<wangguangge@huawei.com> - v1.1.4-1
- Bugfix: fix ai configuration error

* Thu Dec 8 2022 zhuyuncheng<zhuyuncheng@huawei.com> - v1.1.3-3
- Bugfix: fix the alert count error
- Bugfix: for ai model, increase queried data length and add
  a time range for error judgment.

* Wed Dec 7 2022 zhuyuncheng<zhuyuncheng@huawei.com> - v1.1.3-2
- Change default multicheck model

* Wed Dec 7 2022 Lostway<luoshengwei@huawei.com> - v1.1.3-1
- Bugfix: adjust the input parameters of the app

* Mon Dec 5 2022 Lostway<luoshengwei@huawei.com> - v1.1.2-1
- Bugfix: return none when there's no abnormal
- Feature: add model config for each node

* Fri Dec 2 2022 zhuyuncheng<zhuyuncheng@huawei.com> - v1.1.1-2
- Add patch to change model name length limit from 20 to 50 in mysql table

* Fri Dec 2 2022 zhuyuncheng<zhuyuncheng@huawei.com> - v1.1.1-1
- Fix wrong model config path

* Fri Dec 2 2022 zhuyuncheng<zhuyuncheng@huawei.com> - v1.1.0-1
- Update multi-item check algorithm

* Tue Nov 22 2022 zhuyuncheng<zhuyuncheng@huawei.com> - v1.0.0-1
- Package init
