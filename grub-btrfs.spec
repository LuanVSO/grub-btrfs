%define dracutlibdir %{_prefix}/lib/dracut
%global commit 38cd2fa419e4c1c0f1e345a374b37c040c170047
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global commitdate 20260824

Name:           grub-btrfs
Version:        4.14^%{commitdate}git.%{shortcommit}
Release:        %autorelease
Summary:        Adds a btrfs snapshots sub-menu to grub
License:        GPL-3.0-only
URL:            https://github.com/Antynea/grub-btrfs
Source0:        %{url}/archive/%{commit}/%{name}-%{shortcommit}.tar.gz
Source1:        10-grub-btrfs.conf
Source2:        20-grub-btrfs.preset
Patch0:         00-fedora-fix-ups.patch

BuildArch:      noarch
BuildRequires:  make
BuildRequires:  systemd-rpm-macros
Requires:       btrfs-progs
Requires:       grub2
Requires:       bash
Recommends:     snapper
Recommends:     inotify-tools
Enhances:       grub2

%description
grub-btrfs improves the grub bootloader by adding a btrfs snapshots sub-menu,
allowing the user to boot into snapshots.
grub-btrfs supports manual snapshots as well as snapper, timeshift, and yabsnap
created snapshots.

%prep
%autosetup -p1 -n %{name}-%{commit}

%build

%install
%make_install SYSTEMD=true GRUB_UPDATE_EXCLUDE=true
mkdir -p %{buildroot}%{dracutlibdir}/dracut.conf.d
install -Dm0644 %{SOURCE1} %{buildroot}%{dracutlibdir}/dracut.conf.d/10-grub-btrfs.conf
install -Dm0644 %{SOURCE2} %{buildroot}%{_presetdir}/20-grub-btrfs.preset

%post
%systemd_post grub-btrfsd.service

%preun
%systemd_preun grub-btrfsd.service

%postun
%systemd_postun grub-btrfsd.service
 %{_sbindir}/grub2-mkconfig -o /etc/grub2.cfg || :

%posttrans
if [ $1 -eq 1 ]; then
    %{_sbindir}/grub2-mkconfig -o /etc/grub2.cfg >/dev/null || :
    %{_sbindir}/dracut -f || :
fi

%check

%files
%license LICENSE
%doc README.md
%{_docdir}/grub-btrfs/initramfs-overlayfs.md
%{_mandir}/man8/grub-btrfs{,d}.8*
%attr(0700,root,root) %dir %{_sysconfdir}/default/grub-btrfs
%config(noreplace) %{_sysconfdir}/default/grub-btrfs/config
%attr(0755,root,root) %config %{_sysconfdir}/grub.d/41_snapshots-btrfs
%attr(0755,root,root) %{_bindir}/grub-btrfsd
%attr(0644,root,root) %{_unitdir}/grub-btrfsd.service
%attr(0644,root,root) %ghost %config(noreplace) /boot/grub2/grub-btrfs.cfg
%{_presetdir}/20-grub-btrfs.preset
%{dracutlibdir}/dracut.conf.d/10-grub-btrfs.conf

%changelog
%autochangelog
